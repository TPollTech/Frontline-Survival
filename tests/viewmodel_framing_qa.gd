extends SceneTree
## Same camera and neutral poses as the actual player, rendered for every weapon.
const GUNS: Array[String] = ["pistol", "smg", "rifle", "shotgun", "lmg", "sentinela", "sniper", "bolt_sniper"]
const CELL := Vector2i(640, 360)
var failures: Array[String] = []

func _initialize() -> void:
    call_deferred("_run")

func _expect(ok: bool, message: String) -> void:
    if not ok:
        failures.append(message)
        push_error("FRAMING_QA_ERROR: " + message)

func _run() -> void:
    var settings: Variant = root.get_node("GameSettings")
    var previous_fov: float = settings.field_of_view
    settings.field_of_view = 76.0
    var scene: PackedScene = load("res://scenes/main.tscn")
    var game: Variant = scene.instantiate()
    var checkpoint := OS.get_temp_dir().path_join("frontline-framing-%s.save" % OS.get_process_id())
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
    var sheet := Image.create(CELL.x * 2, CELL.y * GUNS.size(), false, Image.FORMAT_RGBA8)
    var rendered_mode := DisplayServer.get_name() != "headless"
    for index in range(GUNS.size()):
        var id: String = GUNS[index]
        player.equip(id)
        _expect(is_instance_valid(player.weapon_model), "missing imported body " + id)
        _expect(player.viewmodel_rear_extent > 0.0, "rear mesh bounds not measured " + id)
        player.equip_anim_timer = 0.0
        player.pending_weapon_id = ""
        player.reloading = false
        player.shot_anim = 0.0
        player.bolt_cycle_remaining = 0.0
        player.sprint_blend = 0.0
        player.walk_anim_blend = 0.0
        player.walk_clock = 0.0
        player.idle_clock = 0.0
        player.weapon_wall_blend = 0.0
        player.gun.rotation = Vector3.ZERO
        player.viewmodel_root.position = Vector3.ZERO
        player.viewmodel_root.rotation = Vector3.ZERO
        for column in range(2):
            var ads: bool = column == 1
            player.aim = ads
            player.camera.fov = player.get_target_camera_fov(false)
            player.gun.position = player.get_viewmodel_rest_pose(ads)
            player._animate_viewmodel(0.25, 0.0)
            var reference: Vector3 = player.gun.position + Vector3(0.0, 0.0, player.viewmodel_depth)
            var rear_z: float = reference.z + player.viewmodel_rear_extent
            _expect(rear_z <= -player.camera.near - 0.099, "neutral rear crosses near margin " + id)
            if ads:
                _expect(absf(reference.x) < 0.0001, "ADS not horizontally centered " + id)
                _expect(absf(reference.y + player.viewmodel_scale * player.get_sight_height()) < 0.0001, "ADS sight axis not centered " + id)
            else:
                _expect(is_equal_approx(reference.x / -reference.z, 0.36), "hip horizontal framing drift " + id)
                _expect(is_equal_approx(reference.y / -reference.z, -0.36), "hip vertical framing drift " + id)
            var anchor: Vector3 = player.camera.to_global(reference)
            _expect(not player.camera.is_position_behind(anchor), "reference behind camera " + id)
            if rendered_mode:
                for frame in range(4):
                    await process_frame
                var image := root.get_texture().get_image()
                _expect(not image.is_empty(), "empty OpenGL capture " + id)
                if not image.is_empty():
                    image.resize(CELL.x, CELL.y, Image.INTERPOLATE_BILINEAR)
                    sheet.blit_rect(image, Rect2i(Vector2i.ZERO, CELL), Vector2i(column * CELL.x, index * CELL.y))
        print("FRAMING_QA_WEAPON " + id + " rear=" + str(player.viewmodel_rear_extent))
    if rendered_mode:
        _expect(sheet.save_png("res://docs/qa/weapon_framing.png") == OK, "could not save framing sheet")
    game.free()
    settings.field_of_view = previous_fov
    if FileAccess.file_exists(checkpoint):
        DirAccess.remove_absolute(checkpoint)
    print("QA_FRAMING_PASS" if failures.is_empty() else "QA_FRAMING_FAIL")
    quit(0 if failures.is_empty() else 1)
