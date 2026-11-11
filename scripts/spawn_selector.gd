extends RefCounted
## Lightweight map-agnostic spawn gate. Must be called from physics context.
## Return {"valid": false} when every point is unsafe: retry later, never spawn
## inside the player, a wall, a soldier or close to a physical buy terminal.
const MIN_PLAYER_DISTANCE := 10.0
const MIN_SHOP_DISTANCE := 4.75
const CHECK_RADIUS := 0.72

static func select_position(
        candidates: Array[Vector3],
        stations: Array[Vector3],
        space: PhysicsDirectSpaceState3D,
        player_position: Vector3,
        camera_forward: Vector3
    ) -> Dictionary:
    if candidates.is_empty():
        return {"valid": false}
    var shape := SphereShape3D.new()
    shape.radius = CHECK_RADIUS
    var shape_query := PhysicsShapeQueryParameters3D.new()
    shape_query.shape = shape
    shape_query.collision_mask = 3
    shape_query.collide_with_bodies = true
    shape_query.collide_with_areas = false
    var best_score: float = -100000.0
    var best: Vector3 = Vector3.ZERO
    var found := false
    var forward_flat := Vector3(camera_forward.x, 0.0, camera_forward.z).normalized()
    for candidate in candidates:
        var displacement := candidate - player_position
        displacement.y = 0.0
        var distance := displacement.length()
        if distance < MIN_PLAYER_DISTANCE:
            continue
        var too_close_to_shop := false
        for station in stations:
            if Vector2(candidate.x, candidate.z).distance_to(Vector2(station.x, station.z)) < MIN_SHOP_DISTANCE:
                too_close_to_shop = true
                break
        if too_close_to_shop:
            continue
        shape_query.transform = Transform3D(Basis.IDENTITY, candidate)
        if not space.intersect_shape(shape_query, 1).is_empty():
            continue
        # Prefer off-screen approaches when a valid route exists, while keeping
        # randomness so that players cannot memorize one deterministic entry.
        var direction := displacement.normalized()
        var in_front := forward_flat.dot(direction) > 0.45
        var score: float = randf_range(0.0, 2.0) + distance * 0.015
        if in_front:
            score -= 0.85
        if score > best_score:
            best_score = score
            best = candidate
            found = true
    if not found:
        return {"valid": false}
    return {"valid": true, "position": best}
