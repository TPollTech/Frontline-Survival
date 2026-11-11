extends SceneTree
## CI integration test. Exercises actual Godot scene, enemies and transition
## through two waves, not just a parser/import smoke test.
const SpawnSelector = preload("res://scripts/spawn_selector.gd")
var failures: Array[String] = []
var checked: int = 0

func _initialize() -> void:
    call_deferred("_run_tests")

func _expect(condition: bool, message: String) -> void:
    checked += 1
    if not condition:
        failures.append(message)
        push_error("QA ERROR: " + message)

func _run_tests() -> void:
    var packed: PackedScene = load("res://scenes/main.tscn")
    _expect(packed != null, "main scene loads")
    if packed == null:
        quit(1)
        return
    var game: Node3D = packed.instantiate()
    root.add_child(game)
    await physics_frame
    # The menu deliberately pauses the game until the player starts.
    game.game_menu._start()
    await physics_frame
    _expect(game.phase == "break", "initial phase is preparation")
    _expect(game.wave == 0, "initial wave not yet started")
    _expect(game.player != null, "player was instantiated")
    _expect(game.shops.size() == 3, "physical shops preserved")
    _expect(not "crosshair_h" in game, "no static 2D crosshair in hardcore mode")

    var stations: Array[Vector3] = []
    for station in game.shops:
        stations.append(station["position"])
    var points: Array[Vector3] = [
        Vector3(-22, 1.5, -22), Vector3(0, 1.5, -23), Vector3(22, 1.5, -22),
        Vector3(-23, 1.5, 0), Vector3(23, 1.5, 0),
        Vector3(-22, 1.5, 22), Vector3(0, 1.5, 23), Vector3(22, 1.5, 22)
    ]
    var good_spawns: int = 0
    for i in range(100):
        var result: Dictionary = SpawnSelector.select_position(
            points, stations, game.get_world_3d().direct_space_state,
            game.player.global_position, Vector3.FORWARD
        )
        if result.get("valid", false):
            good_spawns += 1
            var spot: Vector3 = result["position"]
            _expect(spot.distance_to(game.player.global_position) >= 10.0, "spawn too close to player")
            for station in stations:
                _expect(Vector2(spot.x, spot.z).distance_to(Vector2(station.x, station.z)) >= 4.75, "spawn too close to shop")
    _expect(good_spawns == 100, "100 test spawns are valid")
    var blocked: Array[Vector3] = [game.player.global_position]
    var rejected: Dictionary = SpawnSelector.select_position(
        blocked, stations, game.get_world_3d().direct_space_state,
        game.player.global_position, Vector3.FORWARD
    )
    _expect(not rejected.get("valid", true), "overlapping player spawn must be rejected")

    # Run waves with real enemy scenes, but eliminate them immediately to
    # avoid long unattended combat. This tests counters and reward signal.
    for wave_number in [1, 2]:
        game._begin_wave()
        _expect(game.wave == wave_number, "incorrect wave number")
        _expect(game.phase == "wave", "wave did not enter combat")
        var original_total: int = game.spawn_remaining
        var spawned_count: int = 0
        var attempts: int = 0
        while game.spawn_remaining > 0 and attempts < 150:
            await physics_frame
            attempts += 1
            # Existing automatic spawns are also included in the kill count.
            for enemy in get_nodes_in_group("enemies"):
                if is_instance_valid(enemy) and not enemy.dead:
                    enemy.take_damage(100000.0)
                    spawned_count += 1
            if game.spawn_remaining > 0 and game.alive < 12:
                game._spawn_enemy()
        for enemy in get_nodes_in_group("enemies"):
            if is_instance_valid(enemy) and not enemy.dead:
                enemy.take_damage(100000.0)
                spawned_count += 1
        await physics_frame
        _expect(attempts < 150, "wave spawn queue did not drain")
        _expect(game.alive == 0 and game.spawn_remaining == 0, "wave bookkeeping leak")
        _expect(game.phase == "break", "wave did not return to preparation")
        _expect(game.wave == wave_number, "wave number changed unexpectedly")
        _expect(game.wave_kills == original_total, "not every enemy kill was counted once")
        _expect(spawned_count == original_total, "spawn count mismatch")
        _expect(game.break_remaining > 0.0, "preparation timer missing")
    game.queue_free()
    await process_frame
    if failures.is_empty():
        print("QA_RUNTIME_PASS %d assertions, 100 spawn samples, 2 full wave transitions" % checked)
        quit(0)
    else:
        print("QA_RUNTIME_FAIL %s" % str(failures))
        quit(1)
