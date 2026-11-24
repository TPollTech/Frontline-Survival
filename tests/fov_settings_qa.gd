extends SceneTree
## Exercises the real settings menu, config file and player camera.
## The optional OpenGL run saves actual screenshots of the game and slider.
var failures: Array[String] = []

func _initialize() -> void:
    call_deferred("_run")

func _expect(condition: bool, reason: String) -> void:
    if not condition:
        failures.append(reason)
        push_error("FOV_QA_ERROR: " + reason)

func _capture(name: String) -> void:
    if DisplayServer.get_name() == "headless":
        return
    for frame in range(4):
        await process_frame
    var image := root.get_texture().get_image()
    _expect(not image.is_empty(), "empty rendered FOV screenshot " + name)
    if not image.is_empty():
        _expect(image.save_png("res://docs/qa/" + name + ".png") == OK, "cannot save " + name)

func _slider(menu: Variant) -> HSlider:
    return menu.options.find_child("Setting_fov", true, false) as HSlider

func _run() -> void:
    var settings: Variant = root.get_node("GameSettings")
    var original_path: String = settings.settings_path
    var original_fov: float = settings.field_of_view
    var temp: String = OS.get_temp_dir().path_join("frontline-fov-%s.cfg" % OS.get_process_id())
    var checkpoint: String = temp + ".save"
    settings.settings_path = temp
    settings.set_value("fov", 76.0)
    var scene: PackedScene = load("res://scenes/main.tscn")
    var game: Variant = scene.instantiate()
    game.checkpoint_path = checkpoint
    root.add_child(game)
    var menu: Variant = game.game_menu
    var player: Variant = game.player
    _expect(paused and menu.mode == "main", "main menu not active")
    menu._show_options()
    var slider := _slider(menu)
    _expect(slider != null, "FOV slider missing from main menu")
    if slider != null:
        _expect(slider.min_value == 60.0 and slider.max_value == 100.0 and slider.step == 1.0, "incorrect slider range")
        slider.value = 60.0
        _expect(is_equal_approx(settings.field_of_view, 60.0), "slider signal did not change settings")
        _expect(is_equal_approx(player.camera.fov, 60.0), "paused player camera did not receive FOV")
        var cfg := ConfigFile.new()
        _expect(cfg.load(temp) == OK and float(cfg.get_value("controls", "fov", -1.0)) == 60.0, "FOV not saved")
    menu._back_options()
    menu._start()
    await physics_frame
    player.set_physics_process(false)
    player.aim = false
    _expect(player.camera.current and is_equal_approx(player.camera.fov, 60.0), "new game did not use saved FOV")
    await _capture("fov_60")
    menu.open_pause()
    menu._show_options()
    slider = _slider(menu)
    _expect(slider != null and slider.value == 60.0, "pause menu FOV missing or stale")
    if slider != null:
        slider.value = 100.0
        var value_label := menu.options.find_child("Value_fov", true, false) as Label
        _expect(value_label != null and value_label.text == "100°", "FOV label did not update")
        _expect(is_equal_approx(player.camera.fov, 100.0), "pause slider did not update camera")
        await _capture("fov_menu")
    menu._back_options()
    menu.resume()
    _expect(not paused and is_equal_approx(player.camera.fov, 100.0), "resume lost FOV")
    await _capture("fov_100")
    settings.field_of_view = 76.0
    settings._load()
    _expect(is_equal_approx(settings.field_of_view, 100.0), "config reload lost FOV")
    settings.apply()
    for pair in [[-50.0, 60.0], [500.0, 100.0], [NAN, 76.0], [INF, 76.0], ["invalid", 76.0]]:
        settings.set_value("fov", pair[0])
        _expect(is_equal_approx(settings.field_of_view, float(pair[1])), "invalid FOV not normalized")
    settings.set_value("fov", 90.0)
    for id in ["pistol", "smg", "rifle", "shotgun", "lmg", "sentinela", "sniper", "bolt_sniper"]:
        player.equip(id)
        player.aim = false
        _expect(is_equal_approx(player.get_target_camera_fov(false), 90.0), "hip FOV differs for " + id)
        _expect(is_equal_approx(player.get_target_camera_fov(true), 94.05), "sprint FOV differs for " + id)
        player.aim = true
        _expect(is_equal_approx(player.get_target_camera_fov(true), 63.0), "ADS must override sprint for " + id)
    for id in ["sniper", "bolt_sniper"]:
        player.equip(id)
        player.aim = true
        player.weapon_attachments[id]["optic"] = "scope_2x"
        _expect(is_equal_approx(player.get_target_camera_fov(false), 43.2), "2x zoom changed")
        player.weapon_attachments[id]["optic"] = "scope_4x"
        _expect(is_equal_approx(player.get_target_camera_fov(false), 26.1), "4x zoom changed")
    player.equip("sentinela")
    player.aim = true
    player.weapon_attachments["sentinela"]["optic"] = "scope4"
    _expect(is_equal_approx(player.get_target_camera_fov(false), rad_to_deg(2.0 * atan(0.25))), "Sentinela scope projection changed")
    player.aim = false
    player.camera.fov = 81.0
    settings.apply()
    _expect(is_equal_approx(player.camera.fov, 81.0), "unrelated settings interrupted camera transition")
    game.free()
    settings.settings_path = original_path
    settings.field_of_view = original_fov
    settings.apply()
    if FileAccess.file_exists(temp):
        DirAccess.remove_absolute(temp)
    if FileAccess.file_exists(checkpoint):
        DirAccess.remove_absolute(checkpoint)
    print("QA_FOV_PASS" if failures.is_empty() else "QA_FOV_FAIL")
    quit(0 if failures.is_empty() else 1)
