extends SceneTree
## Render exact generated pilot in the real game scene, in a disposable QA session.
func _initialize() -> void:
    call_deferred("_run")

func fail(message: String) -> void:
    push_error("PILOT_GODOT_FAIL " + message)
    quit(1)

func meshes(n: Node, result: Array[MeshInstance3D]) -> void:
    if n is MeshInstance3D and n.mesh != null:
        result.append(n)
    for child in n.get_children():
        meshes(child,result)

func _run() -> void:
    var folder := OS.get_environment("FRONTLINE_PILOT_DIR")
    if folder.is_empty() or DisplayServer.get_name()=="headless":
        fail("rendering and pilot directory required")
        return
    var report: Variant=JSON.parse_string(FileAccess.get_file_as_string(folder.path_join("pilot-report.json")))
    if not report is Dictionary or root.get_node_or_null("GameSettings")==null:
        fail("missing report or game settings")
        return
    root.size=Vector2i(1280,720)
    var game: Variant=(load("res://scenes/main.tscn") as PackedScene).instantiate()
    game.checkpoint_path="user://qa-pilot-"+str(OS.get_process_id())+".save"
    root.add_child(game)
    game.set_process(false)
    game.set_physics_process(false)
    var player: Variant=game.player
    player.set_physics_process(false)
    player.controls_locked=true
    game.game_menu._start()
    game.combat_hud_root.hide()
    player.viewmodel_projection.hide()
    player.camera.make_current()
    var anchor := Node3D.new()
    game.add_child(anchor)
    var forward: Vector3=-player.camera.global_transform.basis.z
    var horizontal:=Vector3(forward.x,0,forward.z).normalized()
    var candidate: Vector3=player.camera.global_position+horizontal*3.0
    await physics_frame
    await physics_frame
    var query:=PhysicsRayQueryParameters3D.create(candidate+Vector3.UP*4.0,candidate-Vector3.UP*12.0,1,[player.get_rid()])
    var hit: Dictionary=anchor.get_world_3d().direct_space_state.intersect_ray(query)
    if hit.is_empty():
        fail("no ground contact for bollard")
        return
    anchor.global_position=hit.position
    var collider:=StaticBody3D.new()
    var shape:=CollisionShape3D.new()
    var box:=BoxShape3D.new()
    box.size=Vector3(.22,.835,.22)
    shape.shape=box
    shape.position=Vector3(0,.4175,0)
    collider.add_child(shape)
    anchor.add_child(collider)
    var collider_id:=box.get_instance_id()
    var rows: Array[Dictionary]=[]
    for level in range(3):
        var path:=folder.path_join("lod"+str(level)+"/asset.glb")
        var expected: Dictionary={}
        for e in report.exports:
            if int(e.level)==level and e.path=="asset.glb":
                expected=e
        if expected.is_empty() or FileAccess.get_sha256(path)!=expected.sha256:
            fail("hash mismatch")
            return
        var d:=GLTFDocument.new()
        var state:=GLTFState.new()
        if d.append_from_file(path,state)!=OK:
            fail("import error")
            return
        var visual:=d.generate_scene(state)
        if visual==null:
            fail("missing scene")
            return
        anchor.add_child(visual)
        var all: Array[MeshInstance3D]=[]
        meshes(visual,all)
        if all.size()!=4:
            fail("mesh hierarchy")
            return
        var triangles:=0
        var bounds:=all[0].global_transform*all[0].mesh.get_aabb()
        for m in all:
            bounds=bounds.merge(m.global_transform*m.mesh.get_aabb())
            for i in range(m.mesh.get_surface_count()):
                var a:=m.mesh.surface_get_arrays(i)
                if a[Mesh.ARRAY_NORMAL]==null or a[Mesh.ARRAY_TEX_UV]==null or a[Mesh.ARRAY_TANGENT]==null or m.mesh.surface_get_material(i)==null:
                    fail("missing explicit render attributes")
                    return
                triangles+=int(a[Mesh.ARRAY_INDEX].size()/3.0) if a[Mesh.ARRAY_INDEX]!=null and a[Mesh.ARRAY_INDEX].size()>0 else int(a[Mesh.ARRAY_VERTEX].size()/3.0)
        if triangles!=int(expected.metrics.triangles) or not bounds.size.is_equal_approx(Vector3(.22,.835,.22)) or shape.shape.get_instance_id()!=collider_id:
            fail("triangles, physical size or independent collider mismatch")
            return
        await process_frame
        await RenderingServer.frame_post_draw
        await process_frame
        await RenderingServer.frame_post_draw
        var image:=root.get_texture().get_image()
        if image.is_empty() or image.save_png(folder.path_join("godot-lod"+str(level)+".png"))!=OK:
            fail("capture failed")
            return
        rows.append({"level":level,"sha256":expected.sha256,"triangles":triangles,"dimensions_m":[bounds.size.x,bounds.size.y,bounds.size.z],"collider_invariant":true,"camera":"native_player","ground_contact":true,"visual_approval":false})
        visual.free()
    var out:=FileAccess.open(folder.path_join("godot-report.json"),FileAccess.WRITE)
    if out==null:
        fail("report output")
        return
    out.store_string(JSON.stringify({"revision":report.revision,"rows":rows,"visual_approval":false,"production_integrated":false}))
    out.close()
    print("PILOT_GODOT_PASS ",rows.size())
    quit(0)
