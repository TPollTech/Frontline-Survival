extends Node3D
## Experimental single-enemy prototype, NOT a replacement of all combatants.
## Source: Quaternius Universal Base Characters, CC0-1.0.
## The bundled GLB includes the 65-bone human rig, not animation clips.
## Movement is intentionally small, driven by the existing enemy AI.
const HUMAN_GLTF: PackedScene = preload("res://assets/characters/quaternius_base_male.glb")

var valid: bool = false
var skeleton: Skeleton3D
var imported_model: Node3D
var gait_clock: float = 0.0
var arm_pose: Dictionary = {}
# Godot's imported Skeleton3D bone poses already contain its REST rotations.
# All custom posing must be composed onto these base rotations or the
# humanoid twists its limbs into unnatural orientations.
var base_bone_rotations: Dictionary = {}

func _ready() -> void:
    imported_model = HUMAN_GLTF.instantiate() as Node3D
    if imported_model == null:
        push_warning("Quaternius character GLB is not an instantiable 3D scene")
        return
    imported_model.name = "Quaternius_Base_Male"
    # Source glTF is 1.81m tall and faces +Z. Combatants face local -Z,
    # with the collider centered around the waist at ground+0.9m.
    imported_model.position = Vector3(0.0, -0.90, 0.0)
    imported_model.rotation.y = PI
    add_child(imported_model)
    skeleton = _find_skeleton(imported_model)
    if skeleton == null:
        push_warning("Imported Quaternius model has no Skeleton3D; keeping legacy soldier")
        imported_model.queue_free()
        return
    for bone_name in ["Head", "spine_03", "upperarm_l", "upperarm_r", "lowerarm_l", "lowerarm_r", "thigh_l", "thigh_r", "calf_l", "calf_r"]:
        if skeleton.find_bone(bone_name) == -1:
            push_warning("Quaternius rig is missing the expected bone: " + bone_name)
            imported_model.queue_free()
            return
    _paint_character_meshes(imported_model)
    for bone_name in ["upperarm_l", "upperarm_r", "lowerarm_l", "lowerarm_r", "thigh_l", "thigh_r", "calf_l", "calf_r", "spine_03"]:
        var bone_index: int = skeleton.find_bone(bone_name)
        if bone_index != -1:
            base_bone_rotations[bone_name] = skeleton.get_bone_pose_rotation(bone_index)
    _pose_weapon_arms()
    _create_tactical_equipment()
    valid = true

func _find_skeleton(root: Node) -> Skeleton3D:
    if root is Skeleton3D:
        return root as Skeleton3D
    for child in root.get_children():
        var found: Skeleton3D = _find_skeleton(child)
        if found != null:
            return found
    return null

func _paint_character_meshes(root: Node) -> void:
    if root is MeshInstance3D:
        var mesh := root as MeshInstance3D
        var material := StandardMaterial3D.new()
        material.roughness = 0.94
        if mesh.name.contains("Eye"):
            material.albedo_color = Color(0.11, 0.15, 0.15)
        elif mesh.name.contains("Eyebrow"):
            material.albedo_color = Color(0.15, 0.17, 0.16)
        else:
            material.albedo_color = Color(0.34, 0.42, 0.35)
        mesh.material_override = material
    for child in root.get_children():
        _paint_character_meshes(child)

func _bone_toward(name: String, direction: Vector3) -> void:
    var idx: int = skeleton.find_bone(name)
    if idx == -1:
        return
    # Compute a relative pose from the imported rig's real rest axis.
    # Setting local Euler angles directly causes broken elbows for retargeted
    # models whose local bone axes differ from the procedural soldier's.
    var global_rest: Transform3D = skeleton.get_bone_global_rest(idx)
    var global_basis: Basis = global_rest.basis.orthonormalized()
    var current_axis: Vector3 = global_basis.y.normalized()
    var target_axis: Vector3 = direction.normalized()
    var rotation_global := Quaternion(current_axis, target_axis)
    var global_rest_quaternion := global_basis.get_rotation_quaternion()
    var relative_pose: Quaternion = global_rest_quaternion.inverse() * rotation_global * global_rest_quaternion
    # Key fix: never overwrite imported rest pose with a naked quaternion.
    # A small delta over the original bone pose keeps elbows, shoulders and
    # skinned mesh physically connected instead of raising arms vertically.
    var safe_delta: Quaternion = Quaternion.IDENTITY.slerp(relative_pose.normalized(), 0.12)
    var base: Quaternion = base_bone_rotations.get(name, skeleton.get_bone_pose_rotation(idx))
    skeleton.set_bone_pose_rotation(idx, (base * safe_delta).normalized())
    arm_pose[name] = safe_delta

func _pose_weapon_arms() -> void:
    # Character's native +Z is forward; imported scene is rotated to -Z.
    # Gun remains attached to the existing combat system, not to this mesh.
    _bone_toward("upperarm_l", Vector3(-0.24, -0.30, 0.43))
    _bone_toward("upperarm_r", Vector3(0.18, -0.27, 0.46))
    _bone_toward("lowerarm_l", Vector3(0.18, -0.12, 0.44))
    _bone_toward("lowerarm_r", Vector3(-0.12, -0.10, 0.40))

func _create_tactical_equipment() -> void:
    # Lightweight original accessories in the character's local -Z forward
    # coordinate system. No MW3 artwork, textures, meshes or emblems used.
    _equip_capsule("TacticalVest", Vector3(0.0, 0.18, -0.14),
        0.29, 0.59, Color(0.18, 0.23, 0.21), Vector3(0.93, 1.0, 0.48))
    _equip_capsule("BallisticHelmet", Vector3(0.0, 0.78, 0.0),
        0.225, 0.26, Color(0.17, 0.22, 0.19), Vector3.ONE)
    _equip_capsule("RearPack", Vector3(0.0, 0.19, 0.18),
        0.19, 0.39, Color(0.13, 0.16, 0.15), Vector3(1.0, 1.0, 0.52))
    _equip_box("HelmetVisor", Vector3(0.0, 0.77, -0.19),
        Vector3(0.29, 0.085, 0.055), Color(0.10, 0.13, 0.13))
    _equip_box("ChestPouch", Vector3(-0.14, 0.13, -0.25),
        Vector3(0.15, 0.14, 0.07), Color(0.15, 0.19, 0.16))
    _equip_box("ChestPouch2", Vector3(0.11, 0.13, -0.25),
        Vector3(0.14, 0.14, 0.07), Color(0.15, 0.19, 0.16))

func _equip_capsule(name_hint: String, location: Vector3, radius: float,
        height: float, color: Color, part_scale: Vector3) -> void:
    var shape := CapsuleMesh.new()
    shape.radius = radius
    shape.height = height
    shape.radial_segments = 12
    shape.rings = 3
    var part := MeshInstance3D.new()
    part.name = name_hint
    part.mesh = shape
    part.position = location
    part.scale = part_scale
    var mat := StandardMaterial3D.new()
    mat.albedo_color = color
    mat.roughness = 0.90
    part.material_override = mat
    add_child(part)

func _equip_box(name_hint: String, location: Vector3, size: Vector3, color: Color) -> void:
    var shape := BoxMesh.new()
    shape.size = size
    var part := MeshInstance3D.new()
    part.name = name_hint
    part.mesh = shape
    part.position = location
    var mat := StandardMaterial3D.new()
    mat.albedo_color = color
    mat.roughness = 0.92
    part.material_override = mat
    add_child(part)

func animate(delta: float, moving: bool, speed: float, weapon_kick: float) -> void:
    if not valid or not is_instance_valid(skeleton):
        return
    gait_clock += delta * maxf(0.0, speed) * 2.6 if moving else 0.0
    var gait := sin(gait_clock) if moving else 0.0
    var leg_swing: float = 0.26 if moving else 0.0
    if moving and speed > 4.0:
        leg_swing = 0.41
    var smooth: float = minf(1.0, delta * 11.0)
    for name in ["thigh_l", "thigh_r"]:
        var idx: int = skeleton.find_bone(name)
        var opposite: float = 1.0 if name == "thigh_l" else -1.0
        var rest: Quaternion = base_bone_rotations.get(name, Quaternion.IDENTITY)
        var target: Quaternion = (rest * Quaternion(Vector3.RIGHT, gait * leg_swing * opposite)).normalized()
        skeleton.set_bone_pose_rotation(
            idx,
            skeleton.get_bone_pose_rotation(idx).slerp(target, smooth)
        )
    for name in ["calf_l", "calf_r"]:
        var idx: int = skeleton.find_bone(name)
        var phase: float = -gait if name == "calf_l" else gait
        var bend := maxf(0.0, phase) * 0.24
        var rest: Quaternion = base_bone_rotations.get(name, Quaternion.IDENTITY)
        var target: Quaternion = (rest * Quaternion(Vector3.RIGHT, bend)).normalized()
        skeleton.set_bone_pose_rotation(
            idx,
            skeleton.get_bone_pose_rotation(idx).slerp(target, smooth)
        )
    # Arm aiming pose stays while firing; recoil gives a small upper-body shift.
    var spine_idx: int = skeleton.find_bone("spine_03")
    var spine_rest: Quaternion = base_bone_rotations.get("spine_03", Quaternion.IDENTITY)
    var spine_target: Quaternion = (spine_rest * Quaternion(Vector3.RIGHT, -0.07 * weapon_kick)).normalized()
    skeleton.set_bone_pose_rotation(
        spine_idx,
        skeleton.get_bone_pose_rotation(spine_idx).slerp(spine_target, smooth)
    )
