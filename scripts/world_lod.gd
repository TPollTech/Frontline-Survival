extends RefCounted
## Explicit LOD for static world assemblies. No physics changes on swap.
const Selector = preload("res://tools/asset_pipeline/runtime/lod_selector.gd")
# Runtime subset of canonical parametric/lod.py BUDGETS["structure"].
# CI checks these values against that source.
const TRIANGLE_CAPS := [20000,8000,2000]
const COLLIDER_CAP := 24
const MATERIAL_CAP := 8
const OBJECT_TRIANGLE_CAPS := [8000,2800,700]
const OBJECT_COLLIDER_CAP := 8
const OBJECT_MATERIAL_CAP := 4
const STARTS: Array[float] = [0.0,12.0,30.0]
const HYSTERESIS := 1.0
const UPDATE_INTERVAL := 0.2

var entries: Array[Dictionary] = []
var elapsed := UPDATE_INTERVAL

func register_barricade(parts: Array[MeshInstance3D], levels: Array[ArrayMesh], blocker: StaticBody3D) -> bool:
    var per_part: Array = []
    for part in parts:
        per_part.append(levels)
    return register_assembly(parts, per_part, blocker, "structure", "barricade", blocker)

func register_assembly(parts: Array[MeshInstance3D], per_part: Array, anchor: Node3D, category: String, family: String, blocker: StaticBody3D = null) -> bool:
    if category not in ["structure","object"] or not is_instance_valid(anchor) or not anchor.is_inside_tree():
        return false
    var caps: Array = TRIANGLE_CAPS if category=="structure" else OBJECT_TRIANGLE_CAPS
    var material_cap: int = MATERIAL_CAP if category=="structure" else OBJECT_MATERIAL_CAP
    var collider_cap: int = COLLIDER_CAP if category=="structure" else OBJECT_COLLIDER_CAP
    if parts.is_empty() or parts.size()!=per_part.size() or parts.size()>material_cap:
        return false
    var collision: CollisionShape3D = null
    if blocker!=null:
        if not blocker.is_inside_tree():
            return false
        var shapes := blocker.find_children("*","CollisionShape3D",true,false)
        if shapes.size()!=1 or shapes.size()>collider_cap:
            return false
        collision = shapes[0]
        if not collision.shape is BoxShape3D or collision.disabled:
            return false
    var metrics: Array[int] = [0,0,0]
    for k in range(parts.size()):
        var part := parts[k]
        var levels: Array = per_part[k]
        if not is_instance_valid(part) or part.skin!=null or levels.size()!=3 or levels.has(null) or part.mesh!=levels[0]:
            return false
        if blocker==null:
            var ancestor: Node = part
            while ancestor!=null:
                if ancestor is CollisionObject3D:
                    return false
                ancestor=ancestor.get_parent()
        var previous := 2147483647
        var ref: AABB = levels[0].get_aabb()
        for i in range(3):
            var mesh: ArrayMesh = levels[i]
            if mesh.get_surface_count()!=1 or mesh.surface_get_primitive_type(0)!=Mesh.PRIMITIVE_TRIANGLES:
                return false
            var count := int(mesh.surface_get_array_index_len(0)/3)
            if count<=0 or count>=previous:
                return false
            previous=count
            metrics[i]+=count
            var actual := mesh.get_aabb()
            for axis in range(3):
                var allowed := maxf(0.000001,ref.size[axis]*0.05)
                if absf(ref.position[axis]-actual.position[axis])>allowed or absf(ref.end[axis]-actual.end[axis])>allowed:
                    return false
    for i in range(3):
        if metrics[i]>caps[i]:
            return false
    var selector = Selector.new()
    if not selector.configure(STARTS,HYSTERESIS):
        return false
    entries.append({"parts":parts.duplicate(),"part_levels":per_part.duplicate(),"levels":per_part[0],
        "anchor":anchor,"blocker":blocker,"shape":collision,"selector":selector,"triangles":metrics,
        "category":category,"family":family,"collision_policy":"existing_box" if blocker!=null else "nonblocking"})
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
        var anchor: Node3D = entry.anchor
        if not is_instance_valid(anchor):
            continue
        var selector = entry.selector
        var before: int = selector.current
        var index: int = selector.select(camera_position.distance_to(anchor.global_position))
        if index < 0 or before == index:
            continue
        # Deliberately only modify visual mesh resources. Material override,
        # transforms, collider resource, body layer/mask remain untouched.
        for k in range(entry.parts.size()):
            var part: MeshInstance3D = entry.parts[k]
            if is_instance_valid(part):
                part.mesh = entry.part_levels[k][index]

func snapshot() -> Array[Dictionary]:
    var rows: Array[Dictionary] = []
    for entry in entries:
        if not is_instance_valid(entry.anchor):
            continue
        rows.append({"category":entry.category,"path":str(entry.anchor.get_path()),"family":entry.family,"collision_policy":entry.collision_policy,
            "level":entry.selector.current,"triangles_by_level":entry.triangles.duplicate(),
            "material_slots":entry.parts.size(),"colliders":1 if entry.blocker!=null else 0,"collision_triangles":0,
            "limits_provisional":true,"hardware_validated":false})
    return rows
