extends SceneTree
## Actual scene composition regression. Run after importing the project.
var checks := 0
var failures := 0

func _initialize() -> void:
    call_deferred("_run")

func expect(ok: bool, label: String) -> void:
    checks += 1
    if not ok:
        failures += 1
        push_error("MAP_LAYOUT_FAIL " + label)

func _run() -> void:
    if root.get_node_or_null("GameSettings") == null:
        push_error("MAP_LAYOUT_FAIL missing autoload")
        quit(1)
        return
    var game: Variant = (load("res://scenes/main.tscn") as PackedScene).instantiate()
    game.checkpoint_path = "user://qa-map-layout-" + str(OS.get_process_id()) + ".save"
    root.add_child(game)
    game.set_process(false)
    game.set_physics_process(false)
    game.player.set_physics_process(false)
    # Independent baseline from the former inline map recipe.
    var expected: Array = [
        [Vector3(0, -0.5, 0), Vector3(52, 1, 52)],
        [Vector3(0, 2.2, -26), Vector3(52, 4.4, 1)],
        [Vector3(0, 2.2, 26), Vector3(52, 4.4, 1)],
        [Vector3(-26, 2.2, 0), Vector3(1, 4.4, 52)],
        [Vector3(26, 2.2, 0), Vector3(1, 4.4, 52)],
        [Vector3(-9, 1.20, -6), Vector3(5.2, 2.4, 2.0)],
        [Vector3(9, 1.00, 6), Vector3(5.5, 2.0, 2.0)],
        [Vector3(-9, 1.10, 8), Vector3(2.2, 2.2, 4.3)],
        [Vector3(10, 0.80, -9), Vector3(2.5, 1.6, 4.0)],
        [Vector3(-2, 0.34, -13), Vector3(3.44, 0.68, 0.39)],
        [Vector3(2, 0.34, 13), Vector3(3.44, 0.68, 0.39)],
        [Vector3(-15, 0.34, 1), Vector3(2.58, 0.68, 0.39)],
        [Vector3(16, 0.34, -1), Vector3(2.58, 0.68, 0.39)],
    ]
    var blockers: Array[StaticBody3D] = []
    for child in game.get_children():
        if child is StaticBody3D:
            blockers.append(child)
    expect(blockers.size() == expected.size(), "13 world blockers")
    for i in range(mini(blockers.size(), expected.size())):
        var body := blockers[i]
        var shapes := body.find_children("*", "CollisionShape3D", true, false)
        expect(body.position.is_equal_approx(expected[i][0]) and body.collision_layer == 1 and body.collision_mask == 0, "blocker transform/layers " + str(i))
        expect(shapes.size() == 1 and shapes[0].shape is BoxShape3D and not shapes[0].disabled and shapes[0].shape.size.is_equal_approx(expected[i][1]), "independent shape " + str(i))
        expect(body.visible == (i < 9), "blocker visibility " + str(i))
    var ground := get_tree_ground()
    expect(ground != null and ground is StaticBody3D and ground == blockers[0] if not blockers.is_empty() else false, "deployment ground")
    if ground != null:
        var floor_mesh := ground.get_child(0) as MeshInstance3D
        var material := floor_mesh.material_override as StandardMaterial3D
        expect(material.albedo_texture != null and material.albedo_texture.resource_path == "res://assets/textures/asphalt.png" and material.uv1_scale.is_equal_approx(Vector3(16,16,1)), "ground material")
    var shop_baseline := [
        ["weapons", "ARMAS", Vector3(-19,0,-19)],
        ["gear", "EQUIPAMENTOS", Vector3(19,0,-19)],
        ["support", "SUPORTE", Vector3(0,0,21)],
    ]
    expect(game.shops.size() == 3, "shop count")
    for i in range(mini(game.shops.size(),3)):
        var shop: Dictionary = game.shops[i]
        expect(shop.id == shop_baseline[i][0] and shop.name == shop_baseline[i][1] and shop.position.is_equal_approx(shop_baseline[i][2]), "shop placement " + str(i))
    var families: Array[String] = []
    for entry in game.world_lod.entries:
        families.append(entry.family)
    var expected_families: Array[String] = []
    for family_count in [["container_corners",4],["barricade",4],["barrel",8],["light_post",4],["shop",3]]:
        for i in range(family_count[1]):
            expected_families.append(family_count[0])
    expect(families == expected_families, "23 LOD assemblies in original order")
    expect(game.player.position.is_equal_approx(Vector3(0,1.7,0)), "initial player location")
    expect(game.briefing_camera.position.is_equal_approx(Vector3(17,9,18)), "briefing camera")
    print("MAP_LAYOUT_QA ", checks - failures, "/", checks)
    quit(1 if failures else 0)

func get_tree_ground() -> Node3D:
    var grounds := get_nodes_in_group("deployment_ground")
    return grounds[0] as Node3D if grounds.size() == 1 else null
