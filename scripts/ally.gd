extends CharacterBody3D
class_name SurvivalAlly
## Allied support soldier with a simple jointed visual rig, distinct blue patches.

var player: SurvivalPlayer
var health: float = 110.0
var lifetime: float = 160.0
var cooldown: float = 0.8
var flash_time: float = 0.0
var gun_kick: float = 0.0
var muzzle: MeshInstance3D
var walk_time: float = 0.0
var left_hip: Node3D
var right_hip: Node3D
var left_knee: Node3D
var right_knee: Node3D
var left_shoulder: Node3D
var right_shoulder: Node3D
var left_elbow: Node3D
var right_elbow: Node3D
var gun_mount: Node3D

func configure(target: SurvivalPlayer) -> void:
    player = target

func _joint(parent: Node3D, at: Vector3, label: String) -> Node3D:
    var j := Node3D.new()
    j.name = label
    j.position = at
    parent.add_child(j)
    return j

func _piece(parent: Node3D, shape: Mesh, at: Vector3, tint: Color, label: String) -> MeshInstance3D:
    var part := MeshInstance3D.new()
    part.name = label
    part.mesh = shape
    part.position = at
    var mat := StandardMaterial3D.new()
    mat.albedo_color = tint
    mat.roughness = 0.88
    part.material_override = mat
    parent.add_child(part)
    return part

func _box(parent: Node3D, at: Vector3, size: Vector3, tint: Color, label: String) -> MeshInstance3D:
    var shape := BoxMesh.new()
    shape.size = size
    return _piece(parent, shape, at, tint, label)

func _capsule(parent: Node3D, at: Vector3, radius: float, height: float, tint: Color, label: String) -> MeshInstance3D:
    var shape := CapsuleMesh.new()
    shape.radius = radius
    shape.height = height
    shape.radial_segments = 10
    shape.rings = 2
    return _piece(parent, shape, at, tint, label)

func _ready() -> void:
    add_to_group("allies")
    collision_layer = 2
    collision_mask = 1
    var hit := CollisionShape3D.new()
    var shape := CapsuleShape3D.new()
    shape.radius = 0.35
    shape.height = 1.8
    hit.shape = shape
    add_child(hit)
    var uniform := Color(0.29, 0.39, 0.36)
    var armor := Color(0.12, 0.26, 0.28)
    var boots := Color(0.09, 0.12, 0.13)
    var patch := Color(0.09, 0.48, 0.66)
    var visual := _joint(self, Vector3.ZERO, "AllyVisual")
    _capsule(visual, Vector3(0, 0.08, 0), 0.30, 0.83, uniform, "Jacket")
    _box(visual, Vector3(0, 0.13, -0.25), Vector3(0.53, 0.52, 0.16), armor, "Armor")
    _box(visual, Vector3(0, 0.12, 0.25), Vector3(0.45, 0.49, 0.18), armor, "Pack")
    _box(visual, Vector3(0, -0.28, 0), Vector3(0.50, 0.15, 0.31), boots, "Belt")
    for x in [-0.14, 0.0, 0.14]:
        _box(visual, Vector3(x, 0.02, -0.35), Vector3(0.115, 0.18, 0.075), armor.darkened(0.22), "Pouch")
    _capsule(visual, Vector3(0, 0.76, 0), 0.20, 0.38, Color(0.54, 0.43, 0.32), "Head")
    _capsule(visual, Vector3(0, 0.89, 0), 0.235, 0.28, armor, "Helmet")
    _box(visual, Vector3(0, 0.79, -0.19), Vector3(0.31, 0.11, 0.075), boots, "Visor")
    _box(visual, Vector3(0, 0.66, -0.155), Vector3(0.29, 0.12, 0.10), uniform.darkened(0.15), "Cover")

    for side in [-1.0, 1.0]:
        var hip := _joint(visual, Vector3(side * 0.19, -0.34, 0), "LeftHip" if side < 0.0 else "RightHip")
        _capsule(hip, Vector3(0, -0.16, 0), 0.14, 0.37, uniform, "Thigh")
        var knee := _joint(hip, Vector3(0, -0.33, 0), "Knee")
        _capsule(knee, Vector3(0, -0.16, 0), 0.12, 0.37, uniform, "Shin")
        _box(knee, Vector3(0, -0.09, -0.135), Vector3(0.19, 0.17, 0.09), armor, "KneePad")
        _box(knee, Vector3(0, -0.35, -0.09), Vector3(0.22, 0.17, 0.31), boots, "Boot")
        if side < 0.0:
            left_hip = hip
            left_knee = knee
        else:
            right_hip = hip
            right_knee = knee
        var shoulder := _joint(visual, Vector3(side * 0.36, 0.31, -0.035), "LeftShoulder" if side < 0.0 else "RightShoulder")
        _capsule(shoulder, Vector3(0, -0.18, 0), 0.12, 0.45, uniform, "UpperArm")
        _box(shoulder, Vector3(0, -0.055, -0.04), Vector3(0.245, 0.17, 0.23), armor, "ShoulderArmor")
        _box(shoulder, Vector3(0, -0.085, -0.165), Vector3(0.13, 0.095, 0.02), patch, "FriendlyPatch")
        var elbow := _joint(shoulder, Vector3(0, -0.33, 0), "Elbow")
        _capsule(elbow, Vector3(0, -0.15, 0), 0.10, 0.35, uniform, "Forearm")
        _box(elbow, Vector3(0, -0.30, -0.02), Vector3(0.16, 0.14, 0.15), boots, "Glove")
        if side < 0.0:
            left_shoulder = shoulder
            left_elbow = elbow
        else:
            right_shoulder = shoulder
            right_elbow = elbow
    gun_mount = _joint(visual, Vector3(0, 0.10, -0.14), "WeaponRig")
    var rifle_source: PackedScene = load("res://assets/models/rifle.glb")
    if rifle_source != null:
        var model := rifle_source.instantiate() as Node3D
        if model != null:
            model.position = Vector3(0.0, -0.06, -0.04)
            model.scale = Vector3.ONE * 0.72
            gun_mount.add_child(model)
    var flash_mesh := CylinderMesh.new()
    flash_mesh.top_radius = 0.005
    flash_mesh.bottom_radius = 0.023
    flash_mesh.height = 0.16
    muzzle = _piece(gun_mount, flash_mesh, Vector3(0.0, -0.02, -0.04 - 0.72 * 0.95), Color(1.0, 0.53, 0.23), "MuzzleFlash")
    muzzle.rotation.x = PI * 0.5
    var flash_mat := muzzle.material_override as StandardMaterial3D
    flash_mat.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
    flash_mat.emission_enabled = true
    flash_mat.emission = Color(1.0, 0.49, 0.17)
    muzzle.visible = false

func _physics_process(delta: float) -> void:
    if not is_instance_valid(player):
        queue_free()
        return
    lifetime -= delta
    if lifetime <= 0.0:
        queue_free()
        return
    cooldown -= delta
    gun_kick = move_toward(gun_kick, 0.0, delta * 6.0)
    flash_time = maxf(0.0, flash_time - delta)
    muzzle.visible = flash_time > 0.0
    var nearest: SurvivalEnemy
    var nearest_distance := 999.0
    for entity in get_tree().get_nodes_in_group("enemies"):
        var candidate := entity as SurvivalEnemy
        if is_instance_valid(candidate) and not candidate.dead:
            var distance := global_position.distance_to(candidate.global_position)
            if distance < nearest_distance:
                nearest = candidate
                nearest_distance = distance
    var destination := player.global_position
    var stand_off := 4.4
    if is_instance_valid(nearest):
        destination = nearest.global_position
        stand_off = 8.0
    var vec := destination - global_position
    vec.y = 0
    if not is_on_floor():
        velocity.y -= 22.0 * delta
    else:
        velocity.y = -0.2
    var move := vec.normalized() if vec.length() > stand_off else Vector3.ZERO
    velocity.x = move.x * 3.65
    velocity.z = move.z * 3.65
    move_and_slide()
    if vec.length() > 0.1:
        rotation.y = lerp_angle(rotation.y, atan2(-vec.x, -vec.z), minf(1.0, delta * 6.0))
    walk_time += delta * 11.0 * move.length()
    var gait := sin(walk_time) * move.length()
    left_hip.rotation.x = lerpf(left_hip.rotation.x, gait * 0.36, minf(1.0, delta * 11.0))
    right_hip.rotation.x = lerpf(right_hip.rotation.x, -gait * 0.36, minf(1.0, delta * 11.0))
    left_knee.rotation.x = lerpf(left_knee.rotation.x, maxf(0.0, -gait) * 0.55, minf(1.0, delta * 11.0))
    right_knee.rotation.x = lerpf(right_knee.rotation.x, maxf(0.0, gait) * 0.55, minf(1.0, delta * 11.0))
    gun_mount.rotation.x = lerpf(gun_mount.rotation.x, gun_kick * 0.09, minf(1.0, delta * 14.0))
    gun_mount.position.z = lerpf(gun_mount.position.z, -0.14 + gun_kick * 0.075, minf(1.0, delta * 13.0))
    var trigger_grip := gun_mount.position + gun_mount.basis * Vector3(0.06, -0.16, 0.03)
    var support_grip := gun_mount.position + gun_mount.basis * Vector3(-0.06, -0.095, -0.40)
    _pose_support_arm(right_shoulder, right_elbow, trigger_grip, 1.0, delta)
    _pose_support_arm(left_shoulder, left_elbow, support_grip, -1.0, delta)
    if is_instance_valid(nearest) and nearest_distance < 23.0 and cooldown <= 0.0:
        var origin := global_position + Vector3(0, 0.40, 0)
        var target := nearest.global_position + Vector3(0, 0.38, 0)
        var ray := PhysicsRayQueryParameters3D.create(origin, target)
        ray.collision_mask = 3
        ray.exclude = [get_rid()]
        var hit := get_world_3d().direct_space_state.intersect_ray(ray)
        if not hit.is_empty() and hit["collider"] == nearest:
            nearest.take_damage(21.0)
            flash_time = 0.045
            gun_kick = 1.0
            cooldown = 0.72

func _pose_support_arm(shoulder: Node3D, elbow: Node3D, grip: Vector3, side: float, delta: float) -> void:
    # Two-handed posture: off-hand holds the fore-end while the right hand
    # follows the trigger. Align both elbow segments each physics frame.
    var elbow_hint := shoulder.position.lerp(grip, 0.53) + Vector3(side * 0.08, -0.035, 0.015)
    var upper_dir := (elbow_hint - shoulder.position).normalized()
    var shoulder_target := Quaternion(Vector3.DOWN, upper_dir)
    shoulder.quaternion = shoulder.quaternion.slerp(shoulder_target, minf(1.0, delta * 13.0))
    var actual_elbow := shoulder.position + shoulder.basis * elbow.position
    var forearm_dir := shoulder.basis.inverse() * (grip - actual_elbow).normalized()
    var elbow_target := Quaternion(Vector3.DOWN, forearm_dir)
    elbow.quaternion = elbow.quaternion.slerp(elbow_target, minf(1.0, delta * 13.0))
