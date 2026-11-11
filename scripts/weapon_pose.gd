extends RefCounted
## Very small deterministic two-bone arm solver for procedural soldiers.
## Shoulder and weapon mount must share the same parent coordinate space.
## Unlike midpoint aim, this solves the elbow point with actual bone lengths,
## preventing inside-out forearms and detached hands when weapons recoil.
static func align_hand(shoulder: Node3D, elbow: Node3D, grip: Vector3, side: float, delta: float) -> void:
    var source: Vector3 = shoulder.position
    var to_grip: Vector3 = grip - source
    if to_grip.length_squared() < 0.0001:
        return
    var upper_length: float = maxf(0.05, elbow.position.length())
    var lower_length: float = 0.34
    var reach: float = clampf(to_grip.length(), 0.08, upper_length + lower_length - 0.004)
    var target_dir: Vector3 = to_grip.normalized()
    # Elbows bend slightly outward, not into the chest or above the head.
    var bend_hint := Vector3(side, -0.27, 0.08)
    bend_hint -= target_dir * bend_hint.dot(target_dir)
    if bend_hint.length_squared() < 0.001:
        bend_hint = Vector3.FORWARD.cross(target_dir)
    bend_hint = bend_hint.normalized()
    var along: float = (reach * reach + upper_length * upper_length - lower_length * lower_length) / (2.0 * reach)
    var height: float = sqrt(maxf(0.0, upper_length * upper_length - along * along))
    var desired_elbow: Vector3 = source + target_dir * along + bend_hint * height
    var shoulder_aim: Quaternion = Quaternion(Vector3.DOWN, (desired_elbow - source).normalized())
    var response: float = minf(1.0, delta * 18.0)
    shoulder.quaternion = shoulder.quaternion.slerp(shoulder_aim, response)
    # Calculate the actual upper segment after blending, not the desired one.
    var actual_elbow: Vector3 = source + shoulder.basis * elbow.position
    var lower_target: Vector3 = grip - actual_elbow
    if lower_target.length_squared() < 0.0001:
        return
    var local_direction: Vector3 = shoulder.basis.inverse() * lower_target.normalized()
    var forearm_aim: Quaternion = Quaternion(Vector3.DOWN, local_direction)
    elbow.quaternion = elbow.quaternion.slerp(forearm_aim, response)
