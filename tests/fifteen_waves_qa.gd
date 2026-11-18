extends SceneTree
## Accelerates the spawn clock and applies scripted damage. All accounting,
## purchases, support calls and transitions run through the game scene.
var failures: Array[String] = []

func _initialize() -> void:
    call_deferred("_run")

func check(ok: bool, message: String) -> void:
    if not ok:
        failures.append(message)
        push_error(message)

func _run() -> void:
    var game: Variant = load("res://scenes/main.tscn").instantiate()
    root.add_child(game)
    await physics_frame
    game.game_menu._start()
    seed(1525)
    for number in range(1, 16):
        var before: int = game.wallet
        var item := (number - 1) % 3
        var price := 300 if item == 0 else 420
        game._open_shop("support")
        game._buy(item)
        check(game.wallet == before - price, "Support purchase failed in wave %d" % number)
        game.break_remaining = 0.0
        await physics_frame
        await physics_frame
        check(game.wave == number and not game.shop_open and not game.player.controls_locked,
            "Wave transition left controls locked or wrong wave")
        if item == 0:
            check(get_nodes_in_group("turrets").size() > 0, "Turret missing")
        elif item == 1:
            game._call_squad()
            check(game.ally_tokens == 0 and get_nodes_in_group("allies").size() == 2, "Squad deployment failed")
        else:
            game._call_airstrike()
            check(game.airstrike_tokens == 0, "Airstrike credit was not consumed")
        var expected: int = game.wave_kills + game.spawn_remaining + game.alive
        for tick in range(600):
            await physics_frame
            game.spawn_clock = 0.0
            for enemy in get_nodes_in_group("enemies"):
                if not enemy.dead:
                    enemy.take_damage(100000.0, "player")
            if game.phase == "break":
                break
        check(game.phase == "break" and game.wave_kills == expected and game.alive == 0,
            "Wave %d did not settle correctly" % number)
        # Advance past the airstrike delay. Retire deployed units between
        # rotations to exercise repeat purchases without hitting active caps.
        for tick in range(65):
            await physics_frame
        for group in ["allies", "turrets"]:
            for unit in get_nodes_in_group(group):
                unit.queue_free()
        await physics_frame
        if not failures.is_empty():
            quit(1)
            return
    game.queue_free()
    await process_frame
    print("QA_15_WAVES_PASS")
    quit(0)
