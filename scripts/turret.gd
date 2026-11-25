extends Node3D
class_name SurvivalTurret

const WorldAssetGeometry = preload("res://scripts/world_asset_geometry.gd")

const ModelSurface = preload("res://scripts/model_surface.gd")

var time_left: float = 115.0
var shot_cooldown: float = 0.0
var barrel: MeshInstance3D

func _ready() -> void:
    var base := MeshInstance3D.new()
    var cylinder := WorldAssetGeometry.cylinder(0.33, 0.42, 0.8)
    base.mesh = cylinder
    base.position.y = 0.42
    add_child(base)
    var mat := StandardMaterial3D.new()
    mat.albedo_color = Color(0.10, 0.45, 0.50)
    base.material_override = mat
    barrel = MeshInstance3D.new()
    var tube := WorldAssetGeometry.machined(Vector3(0.11, 0.11, 0.75))
    barrel.mesh = tube
    barrel.position = Vector3(0, 0.79, -0.35)
    barrel.material_override = mat
    add_child(barrel)
    var light := OmniLight3D.new()
    light.light_color = Color(0.3, 0.9, 1.0)
    light.light_energy = 0.5
    light.omni_range = 2.5
    light.position.y = 0.95
    add_child(light)

func _physics_process(delta: float) -> void:
    # Torretas compradas durante o intervalo guardam seu tempo de combate.
    var game := get_parent()
    if game != null and game.get("phase") == "break":
        return
    time_left -= delta
    if time_left <= 0.0:
        queue_free()
        return
    shot_cooldown -= delta
    if shot_cooldown > 0.0:
        return
    shot_cooldown = 0.15
    var nearest: SurvivalEnemy = null
    var nearest_distance := 16.0
    for target in get_tree().get_nodes_in_group("enemies"):
        if not is_instance_valid(target) or target.dead:
            continue
        var distance := global_position.distance_to(target.global_position)
        if distance >= nearest_distance:
            continue
        var sight := PhysicsRayQueryParameters3D.create(barrel.global_position, target.global_position, 1)
        if get_world_3d().direct_space_state.intersect_ray(sight).is_empty():
            nearest = target
            nearest_distance = distance
    if nearest != null:
        var direction: Vector3 = nearest.global_position - global_position
        direction.y = 0
        if direction.length() > 0.1:
            rotation.y = atan2(-direction.x, -direction.z)
        nearest.take_damage(18.0)
        shot_cooldown = 0.38
