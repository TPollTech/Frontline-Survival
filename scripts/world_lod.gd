extends RefCounted
## Explicit LOD for static barricade assemblies. No physics changes on swap.
const Selector = preload("res://tools/asset_pipeline/runtime/lod_selector.gd")
# Runtime subset of canonical parametric/lod.py BUDGETS["structure"].
# CI checks these values against that source.
const TRIANGLE_CAPS := [20000,8000,2000]
const COLLIDER_CAP := 24
const MATERIAL_CAP := 8
const STARTS: Array[float] = [0.0,12.0,30.0]
const HYSTERESIS := 1.0
const UPDATE_INTERVAL := 0.2

var entries: Array[Dictionary] = []
var elapsed := UPDATE_INTERVAL

func register_barricade(parts: Array[MeshInstance3D], levels: Array[ArrayMesh], blocker: StaticBody3D) -> bool:
    if parts.is_empty() or parts.size() > MATERIAL_CAP or levels.size() != 3 or levels.has(null):
        return false
    if blocker == null or not blocker.is_inside_tree():
        return false
    var shapes := blocker.find_children("*","CollisionShape3D",true,false)
    if shapes.size() != 1 or shapes.size() > COLLIDER_CAP:
        return false
    var collision: CollisionShape3D = shapes[0]
    if not collision.shape is BoxShape3D or collision.disabled:
        return false
    var metrics: Array[int] = []
    var previous := 2147483647
    for i in range(3):
        if levels[i].get_surface_count()!=1:
            return false
        var count := int(levels[i].surface_get_array_index_len(0) / 3) * parts.size()
        if count <= 0 or count >= previous or count > TRIANGLE_CAPS[i]:
            return false
        previous = count
        metrics.append(count)
        var ref := levels[0].get_aabb()
        var actual := levels[i].get_aabb()
        for axis in range(3):
            var allowed := maxf(0.000001, ref.size[axis] * 0.05)
            if absf(ref.position[axis]-actual.position[axis]) > allowed or absf(ref.end[axis]-actual.end[axis]) > allowed:
                return false
    var selector = Selector.new()
    if not selector.configure(STARTS,HYSTERESIS):
        return false
    for part in parts:
        if not is_instance_valid(part) or part.skin != null or part.mesh != levels[0]:
            return false
    entries.append({"parts":parts.duplicate(),"levels":levels.duplicate(),"blocker":blocker,
        "shape":collision,"selector":selector,"triangles":metrics,"category":"structure"})
    return true

func tick(delta: float, camera: Camera3D) -> void:
    if not is_instance_valid(camera):
        return
    elapsed += delta
    if elapsed < UPDATE_INTERVAL:
        return
    elapsed = 0.0
    update_at(camera.global_position)

func update_at(camera_position: Vector3) -> void:
    if not camera_position.is_finite():
        return
    for entry in entries:
        var blocker: StaticBody3D = entry.blocker
        if not is_instance_valid(blocker):
            continue
        var selector = entry.selector
        var before: int = selector.current
        var index: int = selector.select(camera_position.distance_to(blocker.global_position))
        if index < 0 or before == index:
            continue
        # Deliberately only modify visual mesh resources. Material override,
        # transforms, collider resource, body layer/mask remain untouched.
        for part in entry.parts:
            if is_instance_valid(part):
                part.mesh = entry.levels[index]

func snapshot() -> Array[Dictionary]:
    var rows: Array[Dictionary] = []
    for entry in entries:
        if not is_instance_valid(entry.blocker):
            continue
        rows.append({"category":entry.category,"path":str(entry.blocker.get_path()),
            "level":entry.selector.current,"triangles_by_level":entry.triangles.duplicate(),
            "material_slots":entry.parts.size(),"colliders":1,"collision_triangles":0,
            "limits_provisional":true,"hardware_validated":false})
    return rows
