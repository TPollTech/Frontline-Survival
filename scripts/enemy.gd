extends CharacterBody3D
class_name SurvivalEnemy

const GunMaterials = preload("res://scripts/weapon_materials.gd")
const WeaponAudio = preload("res://scripts/weapon_audio.gd")
const ArmPose = preload("res://scripts/weapon_pose.gd")
const ObstacleSteering = preload("res://scripts/obstacle_steering.gd")
## Lightweight articulated procedural soldier; independent hip, knee, shoulder,
## elbow and upper-body pivots. Designed for up to 12 concurrent enemies.

signal defeated(reward: int)
signal loot_dropped(weapon_kind: String, location: Vector3)

var player: SurvivalPlayer
var kind: String = "soldier"
var weapon_class: String = "shotgun"
var wave: int = 1
var health: float = 90.0
var move_speed: float = 3.1
var attack_damage: float = 10.0
var attack_cooldown: float = 0.0
var attack_interval: float = 2.2
var attack_range: float = 17.0
var reward: int = 50
var dead: bool = false
var detour_remaining: float = 0.0
var detour_direction: Vector3 = Vector3.ZERO
var navigation_check: float = 0.15
var stalled_for: float = 0.0
var last_motion_position: Vector3 = Vector3.ZERO
var obstacle_preference: float = 1.0
var hurt_flash: float = 0.0
var hurt_lean: float = 0.0
var stagger_remaining: float = 0.0
var weapon_kick: float = 0.0
var walk_phase: float = 0.0
var flash_time: float = 0.0
var strafe_sign: float = 1.0
var strafe_timer: float = 0.0

var visual_root: Node3D
var torso_pivot: Node3D
var weapon_pivot: Node3D
var head_pivot: Node3D
var left_hip: Node3D
var right_hip: Node3D
var left_knee: Node3D
var right_knee: Node3D
var left_shoulder: Node3D
var right_shoulder: Node3D
var left_elbow: Node3D
var right_elbow: Node3D
var torso_mesh: MeshInstance3D
var muzzle_flash: MeshInstance3D
var shot_audio: AudioStreamPlayer3D
var hit_collider: CollisionShape3D

func configure(enemy_kind: String, wave_num: int, target: SurvivalPlayer, loadout: String = "") -> void:
    kind = enemy_kind
    wave = wave_num
    weapon_class = loadout if loadout != "" else ("shotgun" if wave < 4 else ("smg" if wave < 11 else ("rifle" if wave < 16 else "lmg")))
    if kind == "heavy":
        weapon_class = "lmg"
    player = target
    if kind == "runner":
        health = 75.0
        move_speed = 4.6
        reward = 78
    elif kind == "heavy":
        health = 260.0
        move_speed = 2.0
        reward = 160
    else:
        health = 90.0
        move_speed = 3.0
        reward = 55
    match weapon_class:
        "shotgun":
            attack_damage = 17.0
            attack_interval = 2.30
            attack_range = 7.0
        "smg":
            attack_damage = 6.5
            attack_interval = 0.80
            attack_range = 15.0
        "rifle":
            attack_damage = 9.0
            attack_interval = 1.15
            attack_range = 23.0
        "lmg":
            attack_damage = 12.0 if kind == "heavy" else 9.0
            attack_interval = 0.90
            attack_range = 22.0
    if kind == "heavy":
        attack_interval *= 0.82
    health *= 1.0 + minf(float(wave - 1) * 0.075, 1.25)
    reward += mini(wave * 3, 80)

func _joint(parent: Node3D, location: Vector3, joint_name: String) -> Node3D:
    var joint := Node3D.new()
    joint.name = joint_name
    joint.position = location
    parent.add_child(joint)
    return joint

func _part(parent: Node3D, shape: Mesh, location: Vector3, tint: Color, name_hint: String = "Part", rotation: Vector3 = Vector3.ZERO) -> MeshInstance3D:
    var piece := MeshInstance3D.new()
    piece.name = name_hint
    piece.mesh = shape
    piece.position = location
    piece.rotation = rotation
    var material := StandardMaterial3D.new()
    material.albedo_color = tint
    material.metallic = 0.10
    material.roughness = 0.89
    piece.material_override = material
    parent.add_child(piece)
    return piece

func _box(parent: Node3D, location: Vector3, size: Vector3, tint: Color, name_hint: String = "Equipment") -> MeshInstance3D:
    var shape := BoxMesh.new()
    shape.size = size
    return _part(parent, shape, location, tint, name_hint)

func _capsule(parent: Node3D, location: Vector3, radius: float, height: float, tint: Color, name_hint: String = "Body") -> MeshInstance3D:
    var shape := CapsuleMesh.new()
    shape.radius = radius
    shape.height = height
    shape.radial_segments = 10
    shape.rings = 2
    return _part(parent, shape, location, tint, name_hint)

func _ready() -> void:
    add_to_group("enemies")
    collision_layer = 2
    collision_mask = 1 | 2
    var collider := CollisionShape3D.new()
    var capsule := CapsuleShape3D.new()
    capsule.height = 1.8
    capsule.radius = 0.48 if kind == "heavy" else 0.38
    collider.shape = capsule
    hit_collider = collider
    add_child(collider)
    strafe_sign = -1.0 if randf() < 0.5 else 1.0
    strafe_timer = randf_range(1.4, 2.8)

    var uniform := Color(0.33, 0.40, 0.31)
    var armor_color := Color(0.21, 0.27, 0.23)
    if kind == "runner":
        uniform = Color(0.46, 0.33, 0.24)
        armor_color = Color(0.30, 0.24, 0.19)
    elif kind == "heavy":
        uniform = Color(0.24, 0.33, 0.39)
        armor_color = Color(0.15, 0.21, 0.27)
    elif weapon_class == "shotgun":
        uniform = Color(0.41, 0.38, 0.28)
        armor_color = Color(0.27, 0.28, 0.23)
    elif weapon_class == "rifle":
        uniform = Color(0.26, 0.35, 0.31)
        armor_color = Color(0.15, 0.21, 0.19)
    elif weapon_class == "lmg":
        uniform = Color(0.27, 0.32, 0.37)
        armor_color = Color(0.15, 0.19, 0.24)
    var dark := Color(0.12, 0.15, 0.15)
    var boots := Color(0.10, 0.12, 0.12)
    var skin := Color(0.51, 0.40, 0.30)
    var heavy_scale := 1.16 if kind == "heavy" else 1.0

    visual_root = _joint(self, Vector3.ZERO, "VisualRig")
    torso_pivot = _joint(visual_root, Vector3(0, -0.10, 0), "Spine")
    torso_mesh = _capsule(torso_pivot, Vector3(0, 0.18, 0), 0.30 * heavy_scale, 0.83, uniform, "TacticalJacket")
    # Curved vest silhouette instead of square chest blocks.
    var front_vest := _capsule(torso_pivot, Vector3(0, 0.24, -0.22), 0.31 * heavy_scale, 0.64, armor_color, "FrontArmorPlate")
    front_vest.scale = Vector3(0.87, 1.0, 0.38)
    var back_vest := _capsule(torso_pivot, Vector3(0, 0.23, 0.22), 0.29, 0.61, armor_color, "BackArmorPlate")
    back_vest.scale = Vector3(0.87, 1.0, 0.43)
    _box(torso_pivot, Vector3(0, -0.20, 0), Vector3(0.49, 0.16, 0.30), dark, "UtilityBelt")
    var pack_mesh := _capsule(torso_pivot, Vector3(0, 0.10, 0.32), 0.21, 0.44, armor_color, "Pack")
    pack_mesh.scale.z = 0.56
    for x in [-0.19, -0.06, 0.07, 0.20]:
        _box(torso_pivot, Vector3(x, 0.12, -0.345), Vector3(0.105, 0.19, 0.09), armor_color.darkened(0.20), "MagazinePouch")
    for side in [-1.0, 1.0]:
        _box(torso_pivot, Vector3(side * 0.27, -0.17, -0.10), Vector3(0.14, 0.22, 0.16), dark, "SidePouch")

    head_pivot = _joint(torso_pivot, Vector3(0, 0.64, 0), "NeckHead")
    _capsule(head_pivot, Vector3(0, 0.02, 0), 0.19, 0.36, skin, "Face")
    _capsule(head_pivot, Vector3(0, 0.15, 0.01), 0.225, 0.28, armor_color, "Helmet")
    _box(head_pivot, Vector3(0, 0.035, -0.178), Vector3(0.31, 0.098, 0.07), dark, "EyesVisor")
    _box(head_pivot, Vector3(0, -0.09, -0.14), Vector3(0.29, 0.11, 0.12), uniform.darkened(0.25), "FaceCover")
    _box(head_pivot, Vector3(0, 0.18, -0.20), Vector3(0.25, 0.065, 0.075), dark, "HelmetRim")
    if kind == "heavy":
        _box(torso_pivot, Vector3(0, 0.23, -0.355), Vector3(0.61, 0.41, 0.08), armor_color.lightened(0.10), "ExtraPlate")
        _box(head_pivot, Vector3(0, 0.00, -0.235), Vector3(0.39, 0.24, 0.08), dark, "BallisticMask")

    for side in [-1.0, 1.0]:
        var hip := _joint(visual_root, Vector3(side * 0.19, -0.34, 0), "LeftHip" if side < 0.0 else "RightHip")
        _capsule(hip, Vector3(0, -0.16, 0), 0.15, 0.38, uniform, "Thigh")
        var knee := _joint(hip, Vector3(0, -0.33, 0), "Knee")
        _capsule(knee, Vector3(0, -0.16, 0), 0.125, 0.38, uniform, "Shin")
        _box(knee, Vector3(0, -0.06, -0.13), Vector3(0.20, 0.18, 0.10), armor_color, "KneePad")
        _box(knee, Vector3(0, -0.35, -0.095), Vector3(0.23, 0.16, 0.32), boots, "CombatBoot")
        if side < 0.0:
            left_hip = hip
            left_knee = knee
        else:
            right_hip = hip
            right_knee = knee
        var shoulder := _joint(torso_pivot, Vector3(side * 0.36, 0.39, -0.04), "LeftShoulder" if side < 0.0 else "RightShoulder")
        _capsule(shoulder, Vector3(0, -0.14, 0), 0.125, 0.39, uniform, "UpperArm")
        var guard := _capsule(shoulder, Vector3(0, -0.035, -0.03), 0.15, 0.22, armor_color, "ShoulderGuard")
        guard.scale = Vector3(1.05, 0.70, 0.68)
        var elbow := _joint(shoulder, Vector3(0, -0.33, -0.01), "Elbow")
        _capsule(elbow, Vector3(0, -0.15, 0), 0.10, 0.36, uniform, "Forearm")
        _box(elbow, Vector3(0, -0.30, -0.025), Vector3(0.16, 0.14, 0.16), dark, "Glove")
        if side < 0.0:
            left_shoulder = shoulder
            left_elbow = elbow
        else:
            right_shoulder = shoulder
            right_elbow = elbow

    weapon_pivot = _joint(torso_pivot, Vector3(0, 0.14, -0.25), "HeldWeapon")
    var gun_path := "res://assets/models/%s.glb" % weapon_class
    if ResourceLoader.exists(gun_path):
        var gun_source: PackedScene = load(gun_path)
        if gun_source != null:
            var held := gun_source.instantiate() as Node3D
            if held != null:
                held.name = "WeaponModel"
                held.scale = Vector3.ONE * 0.70
                # Center the stock/trigger between both hands, not off to the right.
                held.position = Vector3(0.0, -0.06, -0.035)
                weapon_pivot.add_child(held)
                GunMaterials.apply_colors(held)
    # A short tapered flash, no giant yellow cube or glowing sphere.
    var muzzle_shape := CylinderMesh.new()
    muzzle_shape.top_radius = 0.005
    muzzle_shape.bottom_radius = 0.024
    muzzle_shape.height = 0.17
    var muzzle_z: float = -0.035 + 0.70 * float({"shotgun": -1.04, "smg": -0.69, "rifle": -0.95, "lmg": -1.13}.get(weapon_class, -0.69))
    muzzle_flash = _part(weapon_pivot, muzzle_shape, Vector3(0.0, -0.04, muzzle_z), Color(1.0, 0.58, 0.25), "MuzzleFlash", Vector3(PI * 0.5, 0, 0))
    shot_audio = WeaponAudio.add_spatial_shot(muzzle_flash, weapon_class)
    var flash_mat := muzzle_flash.material_override as StandardMaterial3D
    flash_mat.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
    flash_mat.emission_enabled = true
    flash_mat.emission = Color(0.95, 0.47, 0.14)
    flash_mat.emission_energy_multiplier = 1.5
    muzzle_flash.visible = false
    attack_cooldown = randf_range(0.8, 1.6)

func _physics_process(delta: float) -> void:
    if dead or not is_instance_valid(player):
        return
    attack_cooldown -= delta
    flash_time = maxf(0.0, flash_time - delta)
    muzzle_flash.visible = flash_time > 0.0
    hurt_flash = maxf(0.0, hurt_flash - delta)
    hurt_lean = move_toward(hurt_lean, 0.0, delta * 2.2)
    stagger_remaining = maxf(0.0, stagger_remaining - delta)
    weapon_kick = move_toward(weapon_kick, 0.0, delta * 6.0)
    var torso_mat := torso_mesh.material_override as StandardMaterial3D
    torso_mat.emission_enabled = hurt_flash > 0.0
    if hurt_flash > 0.0:
        torso_mat.emission = Color(0.62, 0.14, 0.10)
        torso_mat.emission_energy_multiplier = 0.4
    if not is_on_floor():
        velocity.y -= 22.0 * delta
    else:
        velocity.y = -0.2
    if player.dead:
        velocity.x = 0.0
        velocity.z = 0.0
        move_and_slide()
        _animate_body(delta, false)
        return
    var to_player := player.global_position - global_position
    to_player.y = 0
    var distance := to_player.length()
    var direction := to_player.normalized() if distance > 0.1 else Vector3.ZERO
    var goal_distance := 4.5 if kind == "runner" else (10.0 if kind == "heavy" else (5.5 if weapon_class == "shotgun" else 9.0))
    navigation_check -= delta
    if navigation_check <= 0.0:
        navigation_check = randf_range(0.23, 0.36)
        if distance > goal_distance and ObstacleSteering.blocked(self, direction, 2.35):
            obstacle_preference *= -1.0 if randf() < 0.40 else 1.0
            detour_direction = ObstacleSteering.choose_detour(self, direction, obstacle_preference)
            detour_remaining = maxf(detour_remaining, 0.65)
    var visible := _has_sight()
    var chase := distance > goal_distance or not visible
    var steer := direction
    if detour_remaining > 0.0:
        steer = (direction * 0.40 + detour_direction * 0.90).normalized()
    detour_remaining = maxf(0.0, detour_remaining - delta)
    strafe_timer -= delta
    if strafe_timer <= 0.0:
        strafe_sign *= -1.0
        strafe_timer = randf_range(1.5, 2.8)
    if chase and stagger_remaining <= 0.0:
        velocity.x = steer.x * move_speed
        velocity.z = steer.z * move_speed
    elif visible and distance > 4.0 and kind != "heavy" and stagger_remaining <= 0.0:
        var lateral := Vector3(-direction.z, 0, direction.x) * strafe_sign
        velocity.x = lateral.x * 0.85
        velocity.z = lateral.z * 0.85
    else:
        velocity.x = 0.0
        velocity.z = 0.0
    if distance > 0.2:
        rotation.y = lerp_angle(rotation.y, atan2(-direction.x, -direction.z), minf(1.0, delta * 6.0))
    move_and_slide()
    # Detect motion that only looks active on the animation, e.g. a blocked wall.
    var planar_progress := Vector2(
        global_position.x - last_motion_position.x,
        global_position.z - last_motion_position.z
    ).length()
    last_motion_position = global_position
    if chase and stagger_remaining <= 0.0 and planar_progress < 0.18 * delta:
        stalled_for += delta
    else:
        stalled_for = maxf(0.0, stalled_for - delta * 1.9)
    if stalled_for > 0.72:
        obstacle_preference *= -1.0
        detour_direction = ObstacleSteering.choose_detour(self, direction, obstacle_preference)
        detour_remaining = 1.15
        stalled_for = 0.0
    var moving := Vector2(velocity.x, velocity.z).length() > 0.2
    _animate_body(delta, moving)
    if chase and get_slide_collision_count() > 0 and detour_remaining <= 0.0:
        for i in range(get_slide_collision_count()):
            var normal := get_slide_collision(i).get_normal()
            if absf(normal.y) < 0.4:
                var tangent := Vector3(-normal.z, 0, normal.x)
                if tangent.dot(to_player) < 0.0:
                    tangent = -tangent
                detour_direction = tangent.normalized()
                detour_remaining = 1.20
                break
    if attack_cooldown <= 0.0 and stagger_remaining <= 0.0 and distance < attack_range and visible:
        shot_audio.play()
        player.take_damage(attack_damage, global_position)
        flash_time = 0.045
        weapon_kick = 1.0
        _brief_enemy_tracer()
        attack_cooldown = attack_interval

func _brief_enemy_tracer() -> void:
    # Brief, low-alpha shot line for readable incoming fire; no projectile simulation.
    if not is_instance_valid(player) or not is_instance_valid(weapon_pivot):
        return
    if randf() > 0.65:
        return
    var from := weapon_pivot.to_global(muzzle_flash.position)
    var towards := player.global_position + Vector3.UP * 0.35 - from
    if towards.length() <= 0.5:
        return
    var distance := minf(1.0, towards.length())
    var direction := towards.normalized()
    var streak := MeshInstance3D.new()
    var mesh := CylinderMesh.new()
    mesh.top_radius = 0.002
    mesh.bottom_radius = 0.004
    mesh.height = distance
    streak.mesh = mesh
    streak.position = from + direction * (distance * 0.5)
    streak.quaternion = Quaternion(Vector3.UP, direction)
    var mat := StandardMaterial3D.new()
    mat.albedo_color = Color(1.0, 0.50, 0.30, 0.34)
    mat.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
    mat.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
    streak.material_override = mat
    get_parent().add_child(streak)
    var fade := streak.create_tween()
    fade.tween_property(mat, "albedo_color", Color(1.0, 0.50, 0.30, 0.0), 0.10)
    fade.tween_callback(streak.queue_free)

func _animate_body(delta: float, moving: bool) -> void:
    var gait := 0.0
    if moving:
        walk_phase += delta * move_speed * (4.5 if kind == "runner" else 3.6)
        gait = sin(walk_phase)
    var amount := 0.54 if kind == "runner" else (0.27 if kind == "heavy" else 0.40)
    left_hip.rotation.x = lerpf(left_hip.rotation.x, gait * amount, minf(1.0, delta * 12.0))
    right_hip.rotation.x = lerpf(right_hip.rotation.x, -gait * amount, minf(1.0, delta * 12.0))
    left_knee.rotation.x = lerpf(left_knee.rotation.x, maxf(0.0, -gait) * 0.65, minf(1.0, delta * 11.0))
    right_knee.rotation.x = lerpf(right_knee.rotation.x, maxf(0.0, gait) * 0.65, minf(1.0, delta * 11.0))
    # Arms are aligned toward the trigger and support grip each frame.
    # This avoids empty-handed poses when a soldier changes weapon class.
    torso_pivot.rotation.z = lerpf(torso_pivot.rotation.z, hurt_lean + gait * (0.025 if moving else 0.0), minf(1.0, delta * 13.0))
    torso_pivot.rotation.x = lerpf(torso_pivot.rotation.x, 0.12 * absf(hurt_lean), minf(1.0, delta * 10.0))
    head_pivot.rotation.z = lerpf(head_pivot.rotation.z, -hurt_lean * 0.24, minf(1.0, delta * 8.0))
    weapon_pivot.position.z = lerpf(weapon_pivot.position.z, -0.25 + weapon_kick * 0.085, minf(1.0, delta * 14.0))
    weapon_pivot.rotation.x = lerpf(weapon_pivot.rotation.x, weapon_kick * 0.10, minf(1.0, delta * 15.0))
    var foregrip_z: float = float({"shotgun": -0.42, "smg": -0.32, "rifle": -0.42, "lmg": -0.50}.get(weapon_class, -0.40))
    var trigger_grip := weapon_pivot.position + weapon_pivot.basis * Vector3(0.06, -0.17, 0.025)
    var support_grip := weapon_pivot.position + weapon_pivot.basis * Vector3(-0.06, -0.10, foregrip_z)
    ArmPose.align_hand(right_shoulder, right_elbow, trigger_grip, 1.0, delta)
    ArmPose.align_hand(left_shoulder, left_elbow, support_grip, -1.0, delta)

func _has_sight() -> bool:
    if not is_instance_valid(player):
        return false
    var origin := global_position + Vector3.UP * 0.45
    var target := player.global_position + Vector3.UP * 0.35
    var ray := PhysicsRayQueryParameters3D.create(origin, target)
    ray.collision_mask = 3
    ray.exclude = [get_rid()]
    var result := get_world_3d().direct_space_state.intersect_ray(ray)
    return not result.is_empty() and result["collider"] == player

func take_damage(amount: float) -> void:
    if dead:
        return
    health -= amount
    hurt_flash = 0.11
    hurt_lean = clampf(hurt_lean + (1.0 if randf() < 0.5 else -1.0) * amount * 0.0038, -0.24, 0.24)
    stagger_remaining = maxf(stagger_remaining, minf(0.16, amount * 0.004) * (0.18 if kind == "heavy" else 1.0))
    if health <= 0.0:
        dead = true
        collision_layer = 0
        collision_mask = 0
        hit_collider.set_deferred("disabled", true)
        set_physics_process(false)
        # The dropped weapon becomes a separate pickup while the body remains.
        weapon_pivot.visible = false
        add_to_group("fallen_soldiers")
        loot_dropped.emit(weapon_class, global_position)
        defeated.emit(reward)
        var fall := create_tween().set_parallel(true)
        fall.set_trans(Tween.TRANS_CUBIC)
        fall.set_ease(Tween.EASE_IN)
        fall.tween_property(visual_root, "rotation:z", 1.25 if randf() < 0.5 else -1.25, 0.48)
        fall.tween_property(visual_root, "position:y", -0.48, 0.48)
        fall.chain().tween_interval(17.0)
        fall.chain().tween_callback(queue_free)
