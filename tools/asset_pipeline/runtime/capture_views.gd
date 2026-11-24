extends SceneTree
## Read-only inspection of the actual game scene, isolated QA profile.
var output: String
var views: Array[Dictionary] = []

func _initialize() -> void:
    call_deferred("_run")

func _vec(v: Vector3) -> Array:
    return [v.x, v.y, v.z]

func _matrix(t: Transform3D) -> Array:
    return [_vec(t.basis.x), _vec(t.basis.y), _vec(t.basis.z), _vec(t.origin)]

func _meshes(n: Node, excluded: Node, result: Array[MeshInstance3D]) -> void:
    if n == excluded or n.is_queued_for_deletion():
        return
    if n is MeshInstance3D and n.mesh != null and n.is_visible_in_tree():
        result.append(n)
    for c in n.get_children():
        _meshes(c, excluded, result)

func _bounds(meshes: Array[MeshInstance3D]) -> AABB:
    var box := meshes[0].global_transform * meshes[0].mesh.get_aabb()
    for m in meshes:
        box = box.merge(m.global_transform * m.mesh.get_aabb())
    return box

func _capture(id: String, asset: String, camera: Camera3D, context: Dictionary) -> bool:
    camera.make_current()
    await process_frame
    await RenderingServer.frame_post_draw
    await process_frame
    await RenderingServer.frame_post_draw
    if root.get_camera_3d() != camera:
        push_error("RUNTIME_VIEW_FAIL inactive camera " + id)
        return false
    var image := root.get_texture().get_image()
    if image.is_empty() or image.get_width() < 640 or image.get_height() < 360:
        push_error("RUNTIME_VIEW_FAIL empty/small image " + id)
        return false
    var file := id + ".png"
    if image.save_png(output.path_join(file)) != OK:
        push_error("RUNTIME_VIEW_FAIL save " + id)
        return false
    views.append({"id":id,"asset_id":asset,"file":file,"width":image.get_width(),"height":image.get_height(),
        "camera":{"path":str(camera.get_path()),"world_basis_origin":_matrix(camera.global_transform),
        "projection":camera.projection,"fov":camera.fov,"size":camera.size,"near":camera.near,"far":camera.far,
        "keep_aspect":camera.keep_aspect},"context":context})
    print("RUNTIME_VIEW_CAPTURE ",id," ",image.get_size())
    return true

func _run() -> void:
    output = OS.get_environment("FRONTLINE_VIEWS_DIR")
    if output.is_empty() or DisplayServer.get_name() == "headless":
        push_error("RUNTIME_VIEW_FAIL output directory and real display required")
        quit(1)
        return
    if DirAccess.make_dir_recursive_absolute(output) != OK:
        quit(1)
        return
    if root.get_node_or_null("GameSettings") == null:
        push_error("RUNTIME_VIEW_FAIL autoload missing")
        quit(1)
        return
    root.size = Vector2i(1280,720)
    var game: Variant = (load("res://scenes/main.tscn") as PackedScene).instantiate()
    game.checkpoint_path = "user://qa-views-" + str(OS.get_process_id()) + ".save"
    root.add_child(game)
    game.set_process(false)
    game.set_physics_process(false)
    var p: Variant = game.player
    p.set_physics_process(false)
    p.controls_locked = true
    game.game_menu._start()
    game.combat_hud_root.hide()
    p.camera.make_current()
    var ok: bool = await _capture("fps","viewmodel:assembly",p.camera,{"kind":"native_player_camera","hud_hidden":true})
    if not ok:
        quit(1)
        return
    # Exclude the camera-local viewmodel from map captures. Do not replace world geometry.
    p.viewmodel_projection.hide()
    var meshes: Array[MeshInstance3D] = []
    _meshes(game,p,meshes)
    if meshes.size() < 30 or game.shops.size() != 3:
        push_error("RUNTIME_VIEW_FAIL incomplete map")
        quit(1)
        return
    var box := _bounds(meshes)
    var center := box.get_center()
    var inspect := Camera3D.new()
    inspect.name = "QA_InspectionCamera"
    game.add_child(inspect)
    inspect.projection = Camera3D.PROJECTION_ORTHOGONAL
    inspect.keep_aspect = Camera3D.KEEP_HEIGHT
    inspect.near = 0.1
    inspect.far = maxf(300.0, box.size.length()*5.0)
    inspect.size = maxf(box.size.z,box.size.x/(float(root.size.x)/float(root.size.y)))*1.15
    inspect.global_position = center + Vector3.UP*maxf(60.0,box.size.length())
    inspect.look_at(center,Vector3.FORWARD)
    var context := {"kind":"complete_map_inspection","bounds_min_m":_vec(box.position),
        "bounds_max_m":_vec(box.end),"visible_mesh_nodes":meshes.size(),"shops":game.shops.size(),
        "camera_is_qa":true,"excludes_player_viewmodel":true}
    ok = await _capture("map_top","map:campo_de_testes",inspect,context)
    if not ok:
        quit(1)
        return
    inspect.projection = Camera3D.PROJECTION_PERSPECTIVE
    inspect.fov = 50.0
    inspect.global_position = center + Vector3(1,1.2,1).normalized()*box.size.length()*1.45
    inspect.look_at(center,Vector3.UP)
    ok = await _capture("map_overview","map:campo_de_testes",inspect,context)
    if not ok:
        quit(1)
        return
    # Player has only a first-person rig. Use an actual ally for external
    # inspection, not a fabricated player model or a claim of native TPS.
    var ally: Variant = load("res://scripts/ally.gd").new()
    ally.configure(p)
    ally.position = Vector3(2,0.9,-6)
    game.add_child(ally)
    ally.set_physics_process(false)
    var ally_meshes: Array[MeshInstance3D] = []
    _meshes(ally,null,ally_meshes)
    if ally_meshes.is_empty():
        push_error("RUNTIME_VIEW_FAIL missing real ally model")
        quit(1)
        return
    var ally_box := _bounds(ally_meshes)
    var target := ally_box.get_center()
    inspect.fov = 42.0
    inspect.global_position = target + Vector3(1,0.45,1).normalized()*maxf(3.0,ally_box.size.length()*2.0)
    inspect.look_at(target,Vector3.UP)
    ok = await _capture("external_character","ally:legacy",inspect,{"kind":"external_character_inspection","camera_is_qa":true,"native_player_tps":false,"visible_mesh_nodes":ally_meshes.size()})
    if not ok:
        quit(1)
        return
    var report := FileAccess.open(output.path_join("views.json"),FileAccess.WRITE)
    if report == null:
        quit(1)
        return
    report.store_string(JSON.stringify({"schema_version":1,"kind":"frontline_godot_views",
        "revision":OS.get_environment("GITHUB_SHA"),"engine":Engine.get_version_info(),"display":DisplayServer.get_name(),
        "scene":"res://scenes/main.tscn","views":views,"approved":false}))
    report.close()
    print("RUNTIME_VIEWS_PASS ",views.size())
    quit(0)
