extends SceneTree
## Real OpenGL screenshot, not a headless geometry assertion.
## Allows visual inspection of the new minimalist HUD in GitHub/CI.
func _initialize() -> void:
    call_deferred("_capture")

func _capture() -> void:
    var packed: PackedScene = load("res://scenes/main.tscn")
    if packed == null:
        push_error("QA_HUD_SNAPSHOT_FAIL scene missing")
        quit(1)
        return
    var game: Variant = packed.instantiate()
    root.add_child(game)
    await physics_frame
    game.game_menu._start()
    game.phase = "break"
    game.wave = 2
    game.break_duration = 30.0
    game.break_remaining = 28.0
    game.wallet = 3213
    game.kills = 16
    game.player.health = 100.0
    game.player.armor = 35.0
    game.player.weapon_id = "rifle"
    game.player._update_gun_mesh()
    game.banner_timer = 0.0
    game.report_remaining = 0.0
    game.status_timer = 0.0
    game.player.controls_locked = true
    game.player.camera.rotation = Vector3.ZERO
    game._refresh_ui()
    for frame in range(12):
        await process_frame
    # Live UI should not contain visible tinted rectangles beyond temporary
    # interaction prompts; the main event lane must be dormant by default.
    if game.report_background.visible or game.banner_panel.visible:
        push_error("QA_HUD_SNAPSHOT_FAIL inactive central toast is visible")
        quit(1)
        return
    var viewport: Viewport = game.get_viewport()
    var screenshot: Image = viewport.get_texture().get_image()
    if screenshot.is_empty() or screenshot.get_width() < 1000:
        push_error("QA_HUD_SNAPSHOT_FAIL empty or tiny image")
        quit(1)
        return
    var path := ProjectSettings.globalize_path("res://docs/qa/hud_current.png")
    DirAccess.make_dir_recursive_absolute(path.get_base_dir())
    if screenshot.save_png(path) != OK:
        push_error("QA_HUD_SNAPSHOT_FAIL PNG could not be saved")
        quit(1)
        return
    print("QA_HUD_SNAPSHOT_PASS %dx%d %s" % [screenshot.get_width(), screenshot.get_height(), path])
    quit(0)
