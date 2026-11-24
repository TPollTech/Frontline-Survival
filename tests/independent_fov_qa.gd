extends SceneTree
## Verifies the real camera projection, not only setting values.
## Run headless for numerical checks and with OpenGL for comparison images.
const IDS: Array[String] = ["pistol", "smg", "rifle", "shotgun", "lmg", "sentinela", "sniper", "bolt_sniper"]
const CELL := Vector2i(480, 270)
var failures: Array[String] = []

func _initialize() -> void:
    call_deferred("_run")

func _expect(ok: bool, message: String) -> void:
    if not ok:
        failures.append(message)
        push_error("PROJECTION_QA_ERROR: " + message)

func _screen(player: Variant, local: Vector3) -> Vector2:
    return player.camera.unproject_position(player.gun.to_global(local))

func _run() -> void:
    var settings: Variant = root.get_node("GameSettings")
    var old_world: float = settings.field_of_view
    var old_weapon: float = settings.weapon_field_of_view
    settings.field_of_view = 76.0
    settings.weapon_field_of_view = 76.0
    var scene: PackedScene = load("res://scenes/main.tscn")
    var game: Variant = scene.instantiate()
    var checkpoint := OS.get_temp_dir().path_join("frontline-projection-%s.save" % OS.get_process_id())
    game.checkpoint_path = checkpoint
    root.add_child(game)
    game.game_menu._start()
    await physics_frame
    var player: Variant = game.player
    player.controls_locked = true
    player.set_physics_process(false)
    player.camera.rotation = Vector3.ZERO
    player.gun.visible = true
    game.combat_hud_root.hide()
    game.phase = "break"
    game.break_remaining = 300.0
    var visual: bool = DisplayServer.get_name() != "headless"
    var sheet := Image.create(CELL.x * 3, CELL.y * IDS.size(), false, Image.FORMAT_RGBA8)
    for idx in range(IDS.size()):
        var id: String = IDS[idx]
        player.equip(id)
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
        for ads in [false, true]:
            player.aim = ads
            player.gun.position = player.get_viewmodel_rest_pose(ads)
            player._animate_viewmodel(0.25, 0.0)
            player.camera.fov = 76.0 * (0.70 if ads else 1.0)
            player._update_viewmodel_projection(1.0, false, 22.0)
            var sample: Vector3 = Vector3(0.12, 0.10, player.viewmodel_depth - 0.45)
            var second: Vector3 = Vector3(-0.08, -0.12, player.viewmodel_depth - 0.25)
            var baseline := _screen(player, sample)
            var other := _screen(player, second)
            var center: Vector2 = root.get_visible_rect().size * 0.5
            var ray: Vector3 = player.camera.project_ray_normal(center)
            var world_point: Vector3 = player.camera.to_global(Vector3(1.0, 0.0, -3.0))
            var world_baseline: Vector2 = player.camera.unproject_position(world_point)
            for col in range(3):
                var degrees: float = [60.0, 76.0, 100.0][col]
                player.camera.fov = degrees * (0.70 if ads else 1.0)
                player._sync_viewmodel_projection()
                _expect(_screen(player, sample).distance_to(baseline) < 0.1, "weapon screen position changed " + id)
                _expect(_screen(player, second).distance_to(other) < 0.1, "weapon screen size changed " + id)
                _expect(is_equal_approx(player.viewmodel_projection.scale.z, 1.0), "weapon depth changed")
                _expect(player.camera.project_ray_normal(center).distance_to(ray) < 0.0001, "center firing ray changed")
                if col != 1:
                    _expect(player.camera.unproject_position(world_point).distance_to(world_baseline) > 1.0, "world FOV had no effect")
                if visual and not ads:
                    for frame in range(3):
                        await process_frame
                    var image := root.get_texture().get_image()
                    _expect(not image.is_empty(), "empty projection screenshot")
                    if not image.is_empty():
                        image.resize(CELL.x, CELL.y, Image.INTERPOLATE_BILINEAR)
                        sheet.blit_rect(image, Rect2i(Vector2i.ZERO, CELL), Vector2i(col * CELL.x, idx * CELL.y))
            var before: float = player.camera.fov
            settings.weapon_field_of_view = 95.0
            player._update_viewmodel_projection(1.0, false, 22.0)
            _expect(is_equal_approx(player.camera.fov, before), "weapon setting changed camera")
            _expect(_screen(player, sample).distance_to(baseline) > 1.0, "weapon setting did not change projection")
            settings.weapon_field_of_view = 76.0
            player._update_viewmodel_projection(1.0, false, 22.0)
    if visual:
        _expect(sheet.save_png("res://docs/qa/independent_fov.png") == OK, "could not save FOV comparison")
    game.free()
    settings.field_of_view = old_world
    settings.weapon_field_of_view = old_weapon
    if FileAccess.file_exists(checkpoint):
        DirAccess.remove_absolute(checkpoint)
    print("QA_PROJECTION_PASS" if failures.is_empty() else "QA_PROJECTION_FAIL")
    quit(0 if failures.is_empty() else 1)
