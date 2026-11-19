extends SceneTree

func _initialize() -> void:
    call_deferred("run")

func run() -> void:
    var scene: PackedScene = load("res://scenes/main.tscn")
    var path := OS.get_temp_dir().path_join("frontline-qa-%s.save" % OS.get_process_id())
    var game: Variant = scene.instantiate()
    game.checkpoint_path = path
    root.add_child(game)
    var ok: bool = paused and game.game_menu.navigation.get_child(1).disabled
    game.game_menu._start()
    game.wallet = 1377
    game.player.equip("rifle")
    game.player.magazines["rifle"] = 7
    game.wave = 3
    game.phase = "wave"
    game._end_wave()
    var credits: int = game.wallet
    game.free()
    game = scene.instantiate()
    game.checkpoint_path = path
    root.add_child(game)
    ok = ok and paused and not game.game_menu.navigation.get_child(1).disabled
    game.game_menu._request("new")
    game.game_menu._cancel_action()
    game.game_menu.navigation.get_child(1).pressed.emit()
    ok = ok and not paused and game.wave == 3 and game.wallet == credits and game.player.weapon_id == "rifle" and game.player.magazines["rifle"] == 7
    game._prepare_pause()
    game.game_menu.open_pause()
    game.game_menu._show_options()
    game.game_menu._back_options()
    ok = ok and paused and game.game_menu.mode == "pause"
    game.game_menu.resume()
    ok = ok and not paused and game.player.camera.current
    game.free()
    DirAccess.remove_absolute(path)
    print("CHECKPOINT_MENU_PASS" if ok else "CHECKPOINT_MENU_FAIL")
    quit(0 if ok else 1)
