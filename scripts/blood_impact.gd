extends Node3D
## Transient low-cost blood droplets for a confirmed hit; no expensive GPU particle system.
## All components clean up after 0.30 seconds to keep memory stable on an iGPU.
const LIFE: float = 0.29
const DROPLETS: int = 7

func _ready() -> void:
    add_to_group("blood_fx")
    var droplet_mesh := SphereMesh.new()
    droplet_mesh.radius = 0.034
    droplet_mesh.height = 0.068
    droplet_mesh.radial_segments = 6
    droplet_mesh.rings = 2
    var blood_mat := StandardMaterial3D.new()
    blood_mat.albedo_color = Color(0.37, 0.018, 0.022, 0.88)
    blood_mat.roughness = 0.92
    blood_mat.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
    blood_mat.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
    for i in range(DROPLETS):
        var droplet := MeshInstance3D.new()
        droplet.mesh = droplet_mesh
        droplet.material_override = blood_mat
        droplet.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
        var direction := Vector3(randf_range(-1.0, 1.0), randf_range(-0.3, 1.0), randf_range(-1.0, 1.0)).normalized()
        droplet.position = Vector3.ZERO
        droplet.scale = Vector3.ONE * randf_range(0.55, 1.25)
        add_child(droplet)
        var time: float = randf_range(0.18, LIFE)
        var travel: float = randf_range(0.15, 0.65)
        var tween := create_tween().set_parallel(true)
        tween.tween_property(droplet, "position", direction * travel + Vector3(0.0, -0.11, 0.0), time)
        tween.tween_property(droplet, "scale", Vector3.ZERO, time)
    var cleanup := create_tween()
    cleanup.tween_interval(LIFE + 0.05)
    cleanup.tween_callback(queue_free)
