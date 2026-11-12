extends RigidBody3D
class_name SurvivalFragGrenade
## Offline, original grenade projectile. Godot physics owns flight and bounces.
## CC0 recorded explosion optional: assets/audio/explosions/grenade.ogg.
signal detonated(targets_hit: int)

const FUSE_SECONDS := 2.45
const BLAST_RADIUS := 6.8
const MAX_DAMAGE := 220.0
const BODY_RADIUS := 0.115
const EFFECT_LIFETIME := 1.35
var shooter: SurvivalPlayer
var attack_event: int = 0
var fuse_remaining: float = FUSE_SECONDS
var exploded: bool = false
var targets_hit: int = 0
var body_model: Node3D
var explosion_sound: AudioStreamPlayer3D

func configure(thrower: SurvivalPlayer, event_id: int) -> void:
    shooter = thrower
    attack_event = event_id

func _ready() -> void:
    name = "ThrownFragmentationGrenade"
    add_to_group("live_grenades")
    collision_layer = 8
    collision_mask = 1 # hit world geometry, not the player/NPC colliders
    mass = 0.43
    gravity_scale = 1.0
    continuous_cd = true
    can_sleep = false
    var physical := PhysicsMaterial.new()
    physical.bounce = 0.38
    physical.friction = 0.64
    physics_material_override = physical
    var shape := SphereShape3D.new()
    shape.radius = BODY_RADIUS
    var hitbox := CollisionShape3D.new()
    hitbox.name = "GrenadeCollider"
    hitbox.shape = shape
    add_child(hitbox)
    body_model = Node3D.new()
    body_model.name = "GrenadeModel"
    add_child(body_model)
    _make_body()
    if is_instance_valid(shooter):
        add_collision_exception_with(shooter)
    explosion_sound = AudioStreamPlayer3D.new()
    explosion_sound.name = "ExplosionRecording"
    explosion_sound.volume_db = -9.0
    explosion_sound.max_distance = 65.0
    explosion_sound.unit_size = 10.0
    explosion_sound.bus = "SFX"
    if ResourceLoader.exists("res://assets/audio/explosions/grenade.ogg"):
        explosion_sound.stream = load("res://assets/audio/explosions/grenade.ogg")
    add_child(explosion_sound)

func _make_body() -> void:
    var paint := StandardMaterial3D.new()
    paint.albedo_color = Color(0.19, 0.25, 0.20)
    paint.metallic = 0.43
    paint.roughness = 0.64
    var steel := StandardMaterial3D.new()
    steel.albedo_color = Color(0.48, 0.49, 0.47)
    steel.metallic = 0.82
    steel.roughness = 0.37
    var body := MeshInstance3D.new()
    body.name = "GrenadeShell"
    var shell := CylinderMesh.new()
    shell.top_radius = BODY_RADIUS
    shell.bottom_radius = BODY_RADIUS * 0.92
    shell.height = 0.19
    shell.radial_segments = 12
    body.mesh = shell
    body.material_override = paint
    body_model.add_child(body)
    var cap := MeshInstance3D.new()
    cap.name = "SafetyLever"
    var lever := BoxMesh.new()
    lever.size = Vector3(0.042, 0.15, 0.035)
    cap.mesh = lever
    cap.material_override = steel
    cap.position = Vector3(0.0, 0.10, 0.09)
    cap.rotation.x = 0.24
    body_model.add_child(cap)
    var pin := MeshInstance3D.new()
    pin.name = "PinRing"
    var ring := TorusMesh.new()
    ring.inner_radius = 0.023
    ring.outer_radius = 0.030
    ring.ring_segments = 12
    ring.rings = 8
    pin.mesh = ring
    pin.position = Vector3(0.045, 0.12, 0.0)
    pin.rotation.z = PI * 0.5
    pin.material_override = steel
    body_model.add_child(pin)

func launch(direction: Vector3) -> void:
    var dir := direction.normalized()
    linear_velocity = dir * 18.5 + Vector3.UP * 4.8
    angular_velocity = Vector3(7.0, 4.5, 5.7)

func _physics_process(delta: float) -> void:
    if exploded:
        return
    fuse_remaining = maxf(0.0, fuse_remaining - delta)
    if fuse_remaining <= 0.0:
        _detonate()

func _detonate() -> void:
    if exploded:
        return
    exploded = true
    freeze = true
    linear_velocity = Vector3.ZERO
    angular_velocity = Vector3.ZERO
    collision_layer = 0
    collision_mask = 0
    body_model.visible = false
    var origin := global_position
    targets_hit = _damage_enemies(origin)
    _spawn_explosion_effects()
    if explosion_sound.stream != null:
        explosion_sound.play()
    detonated.emit(targets_hit)
    get_tree().create_timer(EFFECT_LIFETIME).timeout.connect(queue_free)

func _damage_enemies(origin: Vector3) -> int:
    var count: int = 0
    var space := get_world_3d().direct_space_state
    for item in get_tree().get_nodes_in_group("enemies"):
        var enemy := item as SurvivalEnemy
        if not is_instance_valid(enemy) or enemy.dead:
            continue
        var dist := enemy.global_position.distance_to(origin)
        if dist >= BLAST_RADIUS:
            continue
        # Walls and containers block fragmentation; no "magic" damage through cover.
        var query := PhysicsRayQueryParameters3D.create(
            origin + Vector3.UP * 0.20,
            enemy.global_position + Vector3.UP * 0.35
        )
        query.collision_mask = 1
        var block := space.intersect_ray(query)
        if not block.is_empty():
            continue
        var multiplier: float = 1.0 - dist / BLAST_RADIUS
        enemy.take_damage(MAX_DAMAGE * (0.18 + 0.82 * multiplier), "grenade", false, attack_event)
        count += 1
    return count

func _effect_sphere(label: String, tint: Color, radius: float) -> MeshInstance3D:
    var mesh := SphereMesh.new()
    mesh.radius = radius
    mesh.height = radius * 2.0
    mesh.radial_segments = 12
    mesh.rings = 6
    var instance := MeshInstance3D.new()
    instance.name = label
    instance.mesh = mesh
    var mat := StandardMaterial3D.new()
    mat.albedo_color = tint
    mat.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
    mat.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
    mat.cull_mode = BaseMaterial3D.CULL_DISABLED
    instance.material_override = mat
    add_child(instance)
    return instance

func _spawn_explosion_effects() -> void:
    # Brief light, rapidly-expanding shock ring, 10 smoke puffs and 12 sparks.
    # One event, <25 temporary tiny meshes, no expensive particle simulation.
    var flash := _effect_sphere("BlastFlash", Color(1.0, 0.65, 0.24, 0.87), 0.55)
    var flash_tween := create_tween().set_parallel(true)
    flash_tween.tween_property(flash, "scale", Vector3.ONE * 4.4, 0.19)
    flash_tween.tween_property(flash.material_override, "albedo_color",
        Color(1.0, 0.48, 0.16, 0.0), 0.19)
    var ring := TorusMesh.new()
    ring.inner_radius = 0.91
    ring.outer_radius = 1.0
    ring.ring_segments = 24
    ring.rings = 8
    var wave := MeshInstance3D.new()
    wave.name = "ShockwaveRing"
    wave.mesh = ring
    var ring_mat := StandardMaterial3D.new()
    ring_mat.albedo_color = Color(0.97, 0.73, 0.44, 0.68)
    ring_mat.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
    ring_mat.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
    wave.material_override = ring_mat
    wave.position.y = 0.05
    add_child(wave)
    var ring_tween := create_tween().set_parallel(true)
    ring_tween.tween_property(wave, "scale", Vector3(6.5, 0.5, 6.5), 0.38)
    ring_tween.tween_property(ring_mat, "albedo_color", Color(0.96, 0.70, 0.43, 0.0), 0.38)
    var light := OmniLight3D.new()
    light.name = "BlastLight"
    light.light_color = Color(1.0, 0.52, 0.27)
    light.light_energy = 2.9
    light.omni_range = 7.5
    light.shadow_enabled = false
    add_child(light)
    create_tween().tween_property(light, "light_energy", 0.0, 0.20)
    for index in range(10):
        var puff := _effect_sphere("SmokePuff", Color(0.15, 0.17, 0.18, 0.63), 0.34)
        var angle := TAU * float(index) / 10.0 + randf_range(-0.12, 0.12)
        var direction := Vector3(cos(angle), 0.0, sin(angle))
        puff.position = direction * randf_range(0.05, 0.42)
        var end := direction * randf_range(1.3, 3.0) + Vector3.UP * randf_range(1.0, 2.7)
        var tween := create_tween().set_parallel(true)
        tween.tween_property(puff, "position", end, 0.95)
        tween.tween_property(puff, "scale", Vector3.ONE * randf_range(1.6, 2.6), 0.95)
        tween.tween_property(puff.material_override, "albedo_color",
            Color(0.14, 0.16, 0.17, 0.0), 0.95)
    for index in range(12):
        var spark := _effect_sphere("HotFragment", Color(1.0, 0.58, 0.19, 0.9), 0.045)
        var angle := TAU * float(index) / 12.0 + randf_range(-0.10, 0.10)
        var direction := Vector3(cos(angle), randf_range(0.08, 0.66), sin(angle)).normalized()
        var tween := create_tween().set_parallel(true)
        tween.tween_property(spark, "position", direction * randf_range(2.0, 4.1), 0.43)
        tween.tween_property(spark.material_override, "albedo_color",
            Color(0.8, 0.24, 0.04, 0.0), 0.43)
