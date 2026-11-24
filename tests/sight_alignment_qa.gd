extends SceneTree
## Compare neutral decorative sight pictures in the actual game renderer.
const IDS: Array[String] = ["pistol", "smg", "rifle", "shotgun", "lmg", "sentinela", "sniper", "bolt_sniper"]
const CELL := Vector2i(480, 270)
var failures: Array[String] = []

func _initialize() -> void:
    call_deferred("_run")

func _expect(ok: bool, message: String) -> void:
    if not ok:
        failures.append(message)
        push_error("SIGHT_QA_ERROR: " + message)

func _run() -> void:
    var settings: Variant = root.get_node("GameSettings")
    var old_world: float = settings.field_of_view
    var old_weapon: float = settings.weapon_field_of_view
    settings.field_of_view = 76.0
    settings.weapon_field_of_view = 76.0
    var packed: PackedScene = load("res://scenes/main.tscn")
    var game: Variant = packed.instantiate()
    var checkpoint := OS.get_temp_dir().path_join("frontline-sight-%s.save" % OS.get_process_id())
    game.checkpoint_path = checkpoint
    root.add_child(game)
    game.game_menu._start()
    await physics_frame
    var player: Variant = game.player
    player.controls_locked = true
    player.set_physics_process(false)
    player.camera.rotation = Vector3.ZERO
    game.combat_hud_root.hide()
    game.phase = "break"
    game.break_remaining = 300.0
    var visual: bool = DisplayServer.get_name() != "headless"
    var sheet := Image.create(CELL.x * 4, CELL.y * IDS.size(), false, Image.FORMAT_RGBA8)
    sheet.fill(Color(0.025, 0.03, 0.035))
    var count: int = 0
    for row in range(IDS.size()):
        var id: String = IDS[row]
        player.equip(id)
        var optics: Array[String] = ["", "red_dot", "holo"]
        if id in ["sniper", "bolt_sniper"]:
            optics = ["", "scope_2x", "scope_4x"]
        elif id == "sentinela":
            optics = ["", "red_dot", "holo", "scope4"]
        for col in range(optics.size()):
            var optic: String = optics[col]
            if optic != "":
                _expect(player.install_attachment("optic", optic), "optic install failed " + id + "/" + optic)
            player.pending_weapon_id = ""
            player.equip_anim_timer = 0.0
            player.reloading = false
            player.shot_anim = 0.0
            player.bolt_cycle_remaining = 0.0
            player.walk_clock = 0.0
            player.walk_anim_blend = 0.0
            player.idle_clock = 0.0
            player.sprint_blend = 0.0
            player.weapon_wall_blend = 0.0
            player.gun.rotation = Vector3.ZERO
            player.viewmodel_root.position = Vector3.ZERO
            player.viewmodel_root.rotation = Vector3.ZERO
            player.aim = true
            player.gun.position = player.get_viewmodel_rest_pose(true)
            player._animate_viewmodel(0.25, 0.0)
            # Inspect the physical model before the Sentinela's full-screen scope overlay.
            player.gun.visible = true
            player.scope_mask.hide()
            if optic != "":
                _expect(is_instance_valid(player.optic_reticle), "missing physical visual emitter " + id + "/" + optic)
                if is_instance_valid(player.optic_reticle):
                    player.optic_reticle.visible = true
            var point: Vector3 = player.get_visual_sight_point()
            for world_fov in [60.0, 76.0, 100.0]:
                settings.field_of_view = world_fov
                player.camera.fov = player.get_target_camera_fov(false)
                player._update_viewmodel_projection(1.0, false, 22.0)
                var projected: Vector2 = player.camera.unproject_position(player.viewmodel_root.to_global(point))
                var center: Vector2 = root.get_visible_rect().size * 0.5
                _expect(projected.distance_to(center) < 0.5, "neutral sight center differs " + id + "/" + optic + " at " + str(world_fov))
                if is_instance_valid(player.optic_reticle):
                    var emitter: Vector2 = player.camera.unproject_position(player.optic_reticle.global_position)
                    _expect(emitter.distance_to(center) < 0.5, "actual emitter center differs " + id + "/" + optic)
            settings.field_of_view = 76.0
            player.camera.fov = player.get_target_camera_fov(false)
            player._update_viewmodel_projection(1.0, false, 22.0)
            if visual:
                for frame in range(3):
                    await process_frame
                var image := root.get_texture().get_image()
                _expect(not image.is_empty(), "empty sight capture " + id + "/" + optic)
                if not image.is_empty():
                    image.resize(CELL.x, CELL.y, Image.INTERPOLATE_BILINEAR)
                    sheet.blit_rect(image, Rect2i(Vector2i.ZERO, CELL), Vector2i(col * CELL.x, row * CELL.y))
            count += 1
    _expect(count == 25, "missing weapon/optic combination")
    if visual:
        _expect(sheet.save_png("res://docs/qa/sight_alignment.png") == OK, "could not save sight comparison")
    game.free()
    settings.field_of_view = old_world
    settings.weapon_field_of_view = old_weapon
    if FileAccess.file_exists(checkpoint):
        DirAccess.remove_absolute(checkpoint)
    print("QA_SIGHT_PASS" if failures.is_empty() else "QA_SIGHT_FAIL")
    quit(0 if failures.is_empty() else 1)
