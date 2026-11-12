extends RefCounted
## Local tactical cover sampling, using low-frequency world-geometry probes.
const COVER_RADII = [3.0, 5.0, 7.0]

static func _grounded_candidate(space: PhysicsDirectSpaceState3D, at: Vector3) -> Vector3:
    var ray := PhysicsRayQueryParameters3D.create(at + Vector3.UP * 1.7, at + Vector3.DOWN * 3.7)
    ray.collision_mask = 1
    var result := space.intersect_ray(ray)
    if result.is_empty():
        return Vector3.INF
    return result["position"] + Vector3.UP * 0.9

static func _clear(space: PhysicsDirectSpaceState3D, location: Vector3) -> bool:
    var capsule := CapsuleShape3D.new()
    capsule.height = 1.65
    capsule.radius = 0.35
    var query := PhysicsShapeQueryParameters3D.new()
    query.shape = capsule
    query.transform = Transform3D(Basis.IDENTITY, location)
    query.collision_mask = 1
    return space.intersect_shape(query, 1).is_empty()

static func _hidden_from_player(space: PhysicsDirectSpaceState3D, location: Vector3, target: Vector3) -> bool:
    var ray := PhysicsRayQueryParameters3D.create(location + Vector3.UP * 0.16, target + Vector3.UP * 0.35)
    ray.collision_mask = 1
    return not space.intersect_ray(ray).is_empty()

static func find_cover(body: CharacterBody3D, target: Vector3) -> Dictionary:
    var space := body.get_world_3d().direct_space_state
    var away := body.global_position - target
    away.y = 0.0
    if away.length_squared() < 0.01:
        return {}
    away = away.normalized()
    var sideways := Vector3(-away.z, 0.0, away.x)
    var best_score: float = -INF
    var best_position: Vector3 = Vector3.ZERO
    for radius in COVER_RADII:
        for i in range(8):
            var theta: float = TAU * float(i) / 8.0
            var offset: Vector3 = (away * cos(theta) + sideways * sin(theta)) * float(radius)
            var candidate := _grounded_candidate(space, body.global_position + offset)
            if not candidate.is_finite() or candidate.distance_to(target) < 5.5:
                continue
            # A high container roof may intersect the downray but is not
            # reachable by a soldier without jumping or a navigation mesh.
            if absf(candidate.y - body.global_position.y) > 0.85:
                continue
            if not _clear(space, candidate) or not _hidden_from_player(space, candidate, target):
                continue
            var score: float = 14.0 - body.global_position.distance_to(candidate) + absf(sin(theta)) * 1.5
            if score > best_score:
                best_score = score
                best_position = candidate
    if best_score == -INF:
        return {}
    return {"position": best_position, "score": best_score}

static func find_peek(body: CharacterBody3D, cover_at: Vector3, target: Vector3) -> Vector3:
    var space := body.get_world_3d().direct_space_state
    var towards := target - cover_at
    towards.y = 0.0
    if towards.length_squared() < 0.01:
        return cover_at
    towards = towards.normalized()
    var side := Vector3(-towards.z, 0.0, towards.x)
    for trial in [side * 1.7, -side * 1.7, side * 2.7, -side * 2.7]:
        var candidate := _grounded_candidate(space, cover_at + trial)
        if not candidate.is_finite() or absf(candidate.y - cover_at.y) > 0.85:
            continue
        if _clear(space, candidate) and not _hidden_from_player(space, candidate, target):
            return candidate
    return cover_at

static func magazine_size(gun: String) -> int:
    match gun:
        "shotgun": return 8
        "smg": return 30
        "rifle": return 30
        "lmg": return 60
        _: return 12

static func reload_duration(gun: String) -> float:
    match gun:
        "shotgun": return 2.8
        "smg": return 1.9
        "rifle": return 2.4
        "lmg": return 3.5
        _: return 2.0
