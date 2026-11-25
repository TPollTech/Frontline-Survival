extends SceneTree
## Test existing barricades in the actual game, with the native player camera.
var output: String
var rows: Array[Dictionary] = []
func _initialize() -> void:
    call_deferred("_run")

func fail(msg: String) -> void:
    push_error("WORLD_LOD_FAIL " + msg)
    quit(1)

func _run() -> void:
    output = OS.get_environment("FRONTLINE_LOD_DIR")
    if output.is_empty() or DisplayServer.get_name()=="headless":
        fail("real display and output required")
        return
    DirAccess.make_dir_recursive_absolute(output)
    root.size = Vector2i(1280,720)
    var game: Variant = (load("res://scenes/main.tscn") as PackedScene).instantiate()
    game.checkpoint_path = "user://qa-lod-"+str(OS.get_process_id())+".save"
    root.add_child(game)
    game.game_menu._start()
    game.set_process(false)
    game.set_physics_process(false)
    var p: Variant = game.player
    p.set_physics_process(false)
    p.controls_locked = true
    p.viewmodel_projection.hide()
    game.combat_hud_root.hide()
    var camera: Camera3D = p.camera
    camera.make_current()
    if game.world_lod.entries.size()!=19:
        fail("expected 19 assemblies")
        return
    var transitions := [4.,12.,13.2,30.,31.2,30.,28.8,12.,10.8]
    var wanted := [0,0,1,1,2,2,1,1,0]
    var index := 0
    var captured: Dictionary = {}
    for entry in game.world_lod.entries:
        var body: StaticBody3D = entry.blocker
        var shape: CollisionShape3D = entry.shape
        var shape_id := shape.shape.get_instance_id() if shape!=null else 0
        var body_id := body.get_rid() if body!=null else RID()
        var size: Vector3 = shape.shape.size if shape!=null else Vector3.ZERO
        var transform := shape.global_transform if shape!=null else Transform3D.IDENTITY
        var layer := body.collision_layer if body!=null else 0
        var mask := body.collision_mask if body!=null else 0
        var mats: Array[int] = []
        var transforms: Array[Transform3D] = []
        for part in entry.parts:
            mats.append(part.material_override.get_instance_id())
            transforms.append(part.global_transform)
        # Start each selector from the real initial state at near distance.
        var center: Vector3 = entry.anchor.global_position
        var ray_extent := size.z*.5+.3 if body!=null else 0.5
        await physics_frame
        await physics_frame
        var query := PhysicsRayQueryParameters3D.create(center+Vector3(0,0,ray_extent),center-Vector3(0,0,ray_extent),1)
        var baseline := entry.anchor.get_world_3d().direct_space_state.intersect_ray(query)
        if body!=null and (baseline.is_empty() or baseline.collider!=body):
            fail("baseline blocker ray")
            return
        if body==null and not baseline.is_empty():
            fail("unexpected decorative blocker")
            return
        for step in range(transitions.size()):
            var dist: float = transitions[step]
            # Take the long direction along the map, camera at eye height.
            var sign_z := -1.0 if center.z>0 else 1.0
            var dy := 1.65-center.y
            camera.global_position = center+Vector3(0,dy,sign_z*sqrt(dist*dist-dy*dy))
            camera.look_at(center,Vector3.UP)
            game.world_lod.tick(0.21,camera)
            var level: int = wanted[step]
            if entry.selector.current != level:
                fail("distance/hysteresis mismatch")
                return
            var triangles := 0
            for k in range(entry.parts.size()):
                var part: MeshInstance3D = entry.parts[k]
                if part.mesh!=entry.part_levels[k][level] or part.material_override.get_instance_id()!=mats[k] or part.global_transform!=transforms[k]:
                    fail("visual mismatch")
                    return
                triangles+=int(part.mesh.surface_get_array_index_len(0)/3)
            if triangles!=entry.triangles[level] or (body!=null and (shape.shape.get_instance_id()!=shape_id or body.get_rid()!=body_id or shape.shape.size!=size or shape.global_transform!=transform or shape.disabled or body.collision_layer!=layer or body.collision_mask!=mask)):
                fail("collider or budget changed")
                return
            await physics_frame
            await physics_frame
            var hit:=entry.anchor.get_world_3d().direct_space_state.intersect_ray(query)
            if hit.is_empty()!=baseline.is_empty() or (not hit.is_empty() and (hit.collider!=baseline.collider or hit.position.distance_to(baseline.position)>.002)):
                fail("actual blocker ray changed")
                return
            rows.append({"assembly":index,"family":entry.family,"category":entry.category,"distance_m":dist,"level":level,"triangles":triangles,"collider_size":[size.x,size.y,size.z],"hit_z":hit.position.z if not hit.is_empty() else null,"collision_policy":entry.collision_policy,"shape_id_unchanged":true})
            if not captured.has(entry.family+str(level)) and step in [0,2,4]:
                captured[entry.family+str(level)]=true
                await process_frame
                await RenderingServer.frame_post_draw
                var image:=root.get_texture().get_image()
                if image.is_empty() or image.save_png(output.path_join(entry.family+"-lod"+str(level)+".png"))!=OK:
                    fail("capture")
                    return
        index+=1
    var file:=FileAccess.open(output.path_join("world-lod-report.json"),FileAccess.WRITE)
    if file==null:
        fail("report")
        return
    file.store_string(JSON.stringify({"checks":rows,"assemblies":game.world_lod.snapshot(),"hardware_validated":false}, "  "))
    file.close()
    print("WORLD_LOD_PASS ",rows.size()," real map transitions/rays, 8 independent blockers and 11 nonblocking assemblies")
    quit(0)
