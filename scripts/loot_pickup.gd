extends Node3D
## World pickups from defeated enemies. Short lifetime + hard cap imposed by main.
const GunMaterials = preload("res://scripts/weapon_materials.gd")

var pickup_type: String = "weapon"
var weapon_id: String = "rifle"
var amount: int = 18
var remaining: float = 20.0
var initial_scale: Vector3 = Vector3.ONE

func configure(kind: String, weapon: String, rounds: int = 18) -> void:
    pickup_type = kind
    weapon_id = weapon
    amount = rounds

func _ready() -> void:
    add_to_group("world_loot")
    if pickup_type == "weapon":
        var path := "res://assets/models/%s.glb" % weapon_id
        if ResourceLoader.exists(path):
            var model := (load(path) as PackedScene).instantiate() as Node3D
            if model != null:
                model.scale = Vector3.ONE * 0.46
                model.position.y = 0.21
                add_child(model)
                GunMaterials.apply_colors(model)
    else:
        var box := MeshInstance3D.new()
        var shape := BoxMesh.new()
        shape.size = Vector3(0.32, 0.19, 0.23)
        box.mesh = shape
        box.position.y = 0.12
        var mat := StandardMaterial3D.new()
        mat.albedo_color = Color(0.35, 0.34, 0.24)
        mat.roughness = 0.88
        box.material_override = mat
        add_child(box)
        var band := MeshInstance3D.new()
        var strip := BoxMesh.new()
        strip.size = Vector3(0.08, 0.202, 0.235)
        band.mesh = strip
        band.position = box.position
        var band_mat := StandardMaterial3D.new()
        band_mat.albedo_color = Color(0.75, 0.63, 0.31)
        band.material_override = band_mat
        add_child(band)
    rotation.y = randf_range(-PI, PI)
    initial_scale = scale

func _process(delta: float) -> void:
    remaining -= delta
    if remaining <= 0.0:
        queue_free()
        return
    if remaining < 2.0:
        scale = initial_scale * maxf(0.01, remaining / 2.0)

func prompt() -> String:
    if pickup_type == "ammo":
        return "F  •  PEGAR MUNICAO"
    return "F  •  PEGAR %s" % weapon_id.to_upper()
