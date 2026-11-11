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
    var game: Variant = packed.instantiate()
    root.add_child(game)
    await physics_frame
    # The menu deliberately pauses the game until the player starts.
    game.game_menu._start()
    await physics_frame
    _expect(game.phase == "break", "initial phase is preparation")
    _expect(game.wave == 0, "initial wave not yet started")
    _expect(game.player != null, "player was instantiated")
    _expect(game.shops.size() == 3, "physical shops preserved")
    # Previous release had uncolored GLBs: inspect the actual imported scene
    # material on the pistol and make sure the vertex palette is enabled.
    var model_root: Node = game.player.weapon_model
    _expect(model_root != null, "first-person weapon model exists")
    if model_root != null:
        var pending: Array[Node] = [model_root]
        var found_palette := false
        while not pending.is_empty():
            var part: Node = pending.pop_back()
            if part is MeshInstance3D:
                var mi: MeshInstance3D = part as MeshInstance3D
                if mi.material_override is StandardMaterial3D:
                    var material: StandardMaterial3D = mi.material_override
                    found_palette = found_palette or material.vertex_color_use_as_albedo
            for child in part.get_children():
                pending.append(child)
        _expect(found_palette, "weapon GLB palette was not applied on runtime mesh")
    # Previous allied rigs were broken. Spawn and animate two support soldiers.
    game.ally_tokens = 1
    game._call_squad()
    _expect(get_nodes_in_group("allies").size() == 2, "squad did not deploy two allies")
    for frame in range(12):
        await physics_frame
    _expect(get_nodes_in_group("allies").size() == 2, "allies crashed during procedural animation")
    # Screenshot regression: the support soldier's head must be attached to
    # the torso by a collar and use the same pivot as the helmet/mask.
    for support in get_nodes_in_group("allies"):
        var head: Node3D = support.get_node_or_null("AllyVisual/HeadPivot")
        var neck: Node3D = support.get_node_or_null("AllyVisual/NeckCollar")
        _expect(head != null and neck != null, "support head or collar missing")
        if head != null:
            _expect(head.position.y <= 0.69, "support head disconnected from torso silhouette")
        _expect(is_instance_valid(support.muzzle), "support rifle or muzzle missing")
    var reload_clip: AudioStream = game.player.reload_sound.stream
    _expect(reload_clip != null, "mechanical pistol reload is missing")
    _expect(reload_clip.resource_path.contains("/reloads/"), "old synthesized reload beep restored")

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
    # In addition to sampling the center, move the logical player near every
    # edge point. The selected location must still be safely distant.
    for test_position in points:
        var edge_result: Dictionary = SpawnSelector.select_position(
            points, stations, game.get_world_3d().direct_space_state,
            test_position, Vector3.RIGHT
        )
        _expect(edge_result.get("valid", false), "spawn fails with player on an edge")
        if edge_result.get("valid", false):
            _expect(edge_result["position"].distance_to(test_position) >= 10.0,
                "edge player received a spawn too close")
    var no_safe: Dictionary = SpawnSelector.select_position(
        points, points, game.get_world_3d().direct_space_state,
        game.player.global_position, Vector3.FORWARD
    )
    _expect(not no_safe.get("valid", true), "all guarded points must reject spawning")
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
        print("QA_RUNTIME_PASS %d assertions, 100 spawn samples, 2 wave transitions, armed allies and vertex materials" % checked)
        quit(0)
    else:
        print("QA_RUNTIME_FAIL %s" % str(failures))
        quit(1)
