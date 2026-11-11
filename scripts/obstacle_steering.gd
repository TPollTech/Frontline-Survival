extends RefCounted
## Low-cost local obstacle steering for the test arena, not a full navmesh.
## Probes static level geometry, keeping collision queries inside physics ticks.
const RAY_LENGTH := 2.7

static func blocked(body: CollisionObject3D, direction: Vector3, distance: float = RAY_LENGTH) -> bool:
    if direction.length_squared() < 0.001:
        return false
    var start := body.global_position + Vector3(0.0, 0.20, 0.0)
    var query := PhysicsRayQueryParameters3D.create(start, start + direction.normalized() * distance)
    query.collision_mask = 1
    query.exclude = [body.get_rid()]
    return not body.get_world_3d().direct_space_state.intersect_ray(query).is_empty()

static func choose_detour(body: CollisionObject3D, direction: Vector3, preference: float = 1.0) -> Vector3:
    if direction.length_squared() < 0.001:
        return Vector3.ZERO
    var forward := Vector3(direction.x, 0.0, direction.z).normalized()
    var side := Vector3(-forward.z, 0.0, forward.x)
    var prefer_left := preference >= 0.0
    var first := side if prefer_left else -side
    var second := -first
    # Tangential probes handle walls without demanding a costly navigation mesh.
    for steer in [forward * 0.3 + first, forward * 0.3 + second, first, second]:
        var candidate: Vector3 = steer.normalized()
        if not blocked(body, candidate, 1.90):
            return candidate
    # Back off rather than standing forever or teleporting visibly.
    return -forward
