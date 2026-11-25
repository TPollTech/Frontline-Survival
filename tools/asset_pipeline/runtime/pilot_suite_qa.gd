extends SceneTree
## Render each generated visual pilot in the actual game world, no production changes.
func _initialize() -> void:
    call_deferred("_run")

func fail(message: String) -> void:
    push_error("SUITE_GODOT_FAIL " + message)
    quit(1)

func vec(a: Array) -> Vector3:
    return Vector3(float(a[0]),float(a[1]),float(a[2]))

func meshes(n: Node, result: Array[MeshInstance3D]) -> void:
    if n is MeshInstance3D and n.mesh != null:
        result.append(n)
    for child in n.get_children():
        meshes(child,result)

func bone_key(id: String) -> String:
    return id.to_lower().replace(":","").replace("_","").replace("/","").replace(" ","")

func check_rig(visual: Node, all: Array[MeshInstance3D], rig: Dictionary) -> Dictionary:
    var skeletons := visual.find_children("*","Skeleton3D",true,false)
    if skeletons.size()!=1:
        return {"error":"expected one skeleton"}
    var sk: Skeleton3D=skeletons[0]
    var names: Dictionary={}
    for i in range(sk.get_bone_count()):
        names[bone_key(String(sk.get_bone_name(i)))]=i
    for id in rig.parents:
        var index: int=names.get(bone_key("bone:"+str(id)),-1)
        if index<0:
            return {"error":"missing bone "+str(id)}
        var parent: Variant=rig.parents[id]
        var expected: int=-1 if parent==null else names.get(bone_key("bone:"+str(parent)),-2)
        if sk.get_bone_parent(index)!=expected:
            return {"error":"bone parent mismatch "+str(id)}
    var blended:=0
    for m in all:
        if m.skin==null:
            return {"error":"missing skin"}
        for i in range(m.mesh.get_surface_count()):
            var a:=m.mesh.surface_get_arrays(i)
            var indices: PackedInt32Array=a[Mesh.ARRAY_BONES]
            var weights: PackedFloat32Array=a[Mesh.ARRAY_WEIGHTS]
            if weights.size()!=indices.size() or weights.size()!=a[Mesh.ARRAY_VERTEX].size()*4:
                return {"error":"invalid skin arrays"}
            for j in range(0,weights.size(),4):
                var count:=0
                var total:=0.0
                for k in range(j,j+4):
                    total+=weights[k]
                    if weights[k]>0.00001:
                        count+=1
                        if indices[k]<0 or indices[k]>=m.skin.get_bind_count():
                            return {"error":"invalid bind"}
                if absf(total-1.0)>.0001:
                    return {"error":"weights not normalized"}
                if count>1:
                    blended+=1
    if blended==0:
        return {"error":"no blended vertices"}
    var bone: int=names[bone_key("bone:"+str(rig.pose_bone))]
    var child: int=names[bone_key("bone:"+str(rig.pose_child))]
    sk.force_update_all_bone_transforms()
    var before:=sk.get_bone_global_pose(child).origin
    var rest:=sk.get_bone_pose_rotation(bone)
    sk.set_bone_pose_rotation(bone,rest*Quaternion(Vector3.RIGHT,deg_to_rad(float(rig.pose_degrees))))
    sk.force_update_all_bone_transforms()
    var displacement:=before.distance_to(sk.get_bone_global_pose(child).origin)
    if displacement<.001:
        return {"error":"child did not move"}
    return {"bone_count":sk.get_bone_count(),"mixed_render_vertices":blended,"child_displacement_m":displacement,"posed_bone":rig.pose_bone}

func _run() -> void:
    var directory := OS.get_environment("FRONTLINE_PILOT_DIR")
    var suite: Variant=JSON.parse_string(FileAccess.get_file_as_string(directory.path_join("suite.json")))
    if not suite is Dictionary or DisplayServer.get_name()=="headless" or root.get_node_or_null("GameSettings")==null:
        fail("missing suite, rendering, or game settings")
        return
    root.size=Vector2i(1280,720)
    var game: Variant=(load("res://scenes/main.tscn") as PackedScene).instantiate()
    game.checkpoint_path="user://qa-suite-"+str(OS.get_process_id())+".save"
    root.add_child(game)
    game.set_process(false)
    game.set_physics_process(false)
    var player: Variant=game.player
    player.set_physics_process(false)
    player.controls_locked=true
    game.game_menu._start()
    game.combat_hud_root.hide()
    player.viewmodel_projection.hide()
    var camera: Camera3D=player.camera
    camera.make_current()
    var initial_camera: Transform3D=camera.global_transform
    var forward: Vector3=-initial_camera.basis.z
    var horizontal:=Vector3(forward.x,0,forward.z).normalized()
    await physics_frame
    await physics_frame
    var anchor:=Node3D.new()
    game.add_child(anchor)
    var total:=0
    for name in suite.pilots:
        var folder:=directory.path_join(str(name))
        var report: Variant=JSON.parse_string(FileAccess.get_file_as_string(folder.path_join("pilot-report.json")))
        if not report is Dictionary or report.revision!=suite.revision:
            fail("report mismatch "+str(name))
            return
        var dimensions:=vec(report.contract.dimensions_m)
        var expected_center: Vector3=(vec(report.bounds_min_m)+vec(report.bounds_max_m))*0.5
        # Isolated QA framing; ground-supported categories use actual map physics.
        camera.global_transform=initial_camera
        anchor.global_transform=Transform3D.IDENTITY
        var grounded: bool=report.category in ["character","structure","object","environment","terrain","map","vehicle","collision","geometry_library"]
        var candidate: Vector3=camera.global_position+horizontal*maxf(1.6,dimensions.length()*1.55)
        if grounded:
            var query:=PhysicsRayQueryParameters3D.create(candidate+Vector3.UP*4.0,candidate-Vector3.UP*12.0,1,[player.get_rid()])
            var hit: Dictionary=anchor.get_world_3d().direct_space_state.intersect_ray(query)
            if hit.is_empty():
                fail("ground query "+str(name))
                return
            anchor.global_position=hit.position-Vector3.UP*float(report.bounds_min_m[1])
        else:
            anchor.global_position=camera.global_position+forward*maxf(.38,dimensions.length()*1.55)-expected_center
        # Show the authored front with a modest turn, not the opaque rear wall.
        anchor.look_at(Vector3(camera.global_position.x,anchor.global_position.y,camera.global_position.z),Vector3.UP)
        anchor.rotate_y(.32)
        camera.look_at(anchor.to_global(expected_center),Vector3.UP)
        var body: StaticBody3D = null
        var collider: CollisionShape3D = null
        var collider_id: int = 0
        if report.get("collision") != null:
            body=StaticBody3D.new()
            collider=CollisionShape3D.new()
            var shape:=BoxShape3D.new()
            shape.size=vec(report.collision.size_m)
            collider.shape=shape
            collider.position=vec(report.collision.center_m)
            body.add_child(collider)
            anchor.add_child(body)
            collider_id=shape.get_instance_id()
        var rows: Array[Dictionary]=[]
        for level in range(3):
            var path:=folder.path_join("lod"+str(level)+"/asset.glb")
            var expected: Dictionary={}
            for e in report.exports:
                if int(e.level)==level and e.path=="asset.glb":
                    expected=e
            if expected.is_empty() or FileAccess.get_sha256(path)!=expected.sha256:
                fail("hash mismatch "+str(name))
                return
            var doc:=GLTFDocument.new()
            var state:=GLTFState.new()
            if doc.append_from_file(path,state)!=OK:
                fail("import "+str(name))
                return
            var visual:=doc.generate_scene(state)
            if visual==null:
                fail("missing scene")
                return
            anchor.add_child(visual)
            var all: Array[MeshInstance3D]=[]
            meshes(visual,all)
            if all.is_empty() or all.size()!=int(expected.metrics.mesh_instances):
                fail("mesh hierarchy "+str(name))
                return
            var count:=0
            var bounds:=all[0].global_transform*all[0].mesh.get_aabb()
            var local_bounds:=anchor.global_transform.affine_inverse()*all[0].global_transform*all[0].mesh.get_aabb()
            for m in all:
                bounds=bounds.merge(m.global_transform*m.mesh.get_aabb())
                local_bounds=local_bounds.merge(anchor.global_transform.affine_inverse()*m.global_transform*m.mesh.get_aabb())
                for i in range(m.mesh.get_surface_count()):
                    var a:=m.mesh.surface_get_arrays(i)
                    if a[Mesh.ARRAY_NORMAL]==null or a[Mesh.ARRAY_TEX_UV]==null or a[Mesh.ARRAY_TANGENT]==null or m.mesh.surface_get_material(i)==null:
                        fail("missing render attributes "+str(name))
                        return
                    count+=int(a[Mesh.ARRAY_INDEX].size()/3.0) if a[Mesh.ARRAY_INDEX]!=null and a[Mesh.ARRAY_INDEX].size()>0 else int(a[Mesh.ARRAY_VERTEX].size()/3.0)
            if count!=int(expected.metrics.triangles) or (local_bounds.size-dimensions).abs().length()>.001:
                fail("dimensions/triangles "+str(name)+" "+str(local_bounds.size)+" "+str(dimensions))
                return
            for i in range(8):
                var corner:=bounds.get_endpoint(i)
                var screen:=camera.unproject_position(corner)
                if camera.is_position_behind(corner) or not Rect2(Vector2.ZERO,Vector2(root.size)).has_point(screen):
                    fail("camera clipping "+str(name))
                    return
            if collider != null and (collider.shape.get_instance_id()!=collider_id or not (collider.shape as BoxShape3D).size.is_equal_approx(dimensions)):
                fail("collider contract "+str(name))
                return
            await process_frame
            await RenderingServer.frame_post_draw
            await process_frame
            await RenderingServer.frame_post_draw
            var image:=root.get_texture().get_image()
            if image.is_empty() or image.save_png(folder.path_join("godot-lod"+str(level)+".png"))!=OK:
                fail("capture "+str(name))
                return
            var rig_check: Dictionary={}
            if expected.get("rig")!=null:
                rig_check=check_rig(visual,all,expected.rig)
                if rig_check.has("error"):
                    fail("rig "+str(name)+" "+str(rig_check))
                    return
                await process_frame
                await RenderingServer.frame_post_draw
                var posed_image:=root.get_texture().get_image()
                if posed_image.is_empty() or posed_image.save_png(folder.path_join("godot-pose-lod"+str(level)+".png"))!=OK:
                    fail("posed capture "+str(name))
                    return
                print("SUITE_RIG_PASS ",name," LOD",level," ",rig_check)
            rows.append({"rig":rig_check,"level":level,"sha256":FileAccess.get_sha256(path),"triangles":count,"dimensions_m":[local_bounds.size.x,local_bounds.size.y,local_bounds.size.z],"camera":"native_player_qa_placement","ground_contact_sampled":grounded,"visual_approval":false,"independent_collision_checked":collider!=null})
            visual.free()
            total+=1
        if body!=null:
            body.free()
        var out:=FileAccess.open(folder.path_join("godot-report.json"),FileAccess.WRITE)
        if out==null:
            fail("report output")
            return
        out.store_string(JSON.stringify({"revision":report.revision,"rows":rows,"visual_approval":false,"production_integrated":false}))
        out.close()
        print("SUITE_GODOT_ASSET_PASS ",name," ",rows.size())
    print("SUITE_GODOT_PASS ",total)
    quit(0)
