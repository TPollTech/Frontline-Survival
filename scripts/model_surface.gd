extends RefCounted
## Dimensioned superellipsoids. One indexed surface with shared geometry across instances.
enum Profile { MACHINED, MOLDED, PADDED }
const POWER := [12.0, 5.0, 3.2]
const STEPS := 6
static var cache: Dictionary = {}

static func body(size: Vector3, profile: Profile = Profile.MOLDED) -> ArrayMesh:
    var key := Vector4(size.x, size.y, size.z, float(profile))
    if cache.has(key):
        return cache[key]
    var vertices := PackedVector3Array()
    var normals := PackedVector3Array()
    var uv := PackedVector2Array()
    var indices := PackedInt32Array()
    var distant := PackedInt32Array()
    var exponent: float = POWER[profile]
    for axis in [Vector3.RIGHT, Vector3.LEFT, Vector3.UP, Vector3.DOWN, Vector3.BACK, Vector3.FORWARD]:
        var face: Vector3 = axis
        var tangent := Vector3.RIGHT if absf(face.y) > 0.5 else Vector3.UP
        var across := face.cross(tangent)
        var first := vertices.size()
        for row in range(STEPS + 1):
            for col in range(STEPS + 1):
                var tex := Vector2(col, row) / float(STEPS)
                var q := face + tangent * (tex.x * 2.0 - 1.0) + across * (tex.y * 2.0 - 1.0)
                var norm := pow(pow(absf(q.x), exponent) + pow(absf(q.y), exponent) + pow(absf(q.z), exponent), 1.0 / exponent)
                vertices.append(size * q / (2.0 * norm))
                var gradient := Vector3(pow(absf(q.x), exponent - 1), pow(absf(q.y), exponent - 1), pow(absf(q.z), exponent - 1))
                normals.append((gradient * q.sign() / size).normalized())
                uv.append(tex)
        _grid(indices, first, 1)
        _grid(distant, first, 2)
    var arrays := []
    arrays.resize(Mesh.ARRAY_MAX)
    arrays[Mesh.ARRAY_VERTEX] = vertices
    arrays[Mesh.ARRAY_NORMAL] = normals
    arrays[Mesh.ARRAY_TEX_UV] = uv
    arrays[Mesh.ARRAY_INDEX] = indices
    var mesh := ArrayMesh.new()
    mesh.add_surface_from_arrays(Mesh.PRIMITIVE_TRIANGLES, arrays, [], {size.length() * 0.016: distant})
    cache[key] = mesh
    return mesh

static func _grid(indices: PackedInt32Array, first: int, stride: int) -> void:
    for row in range(0, STEPS, stride):
        for col in range(0, STEPS, stride):
            var a := first + row * (STEPS + 1) + col
            var b := a + stride
            var c := a + stride * (STEPS + 1)
            indices.append_array(PackedInt32Array([a, c, b, b, c, c + stride]))


# Explicit distance LODs, reusing the exact existing authored samples.
# Compact each level so unused vertices are not uploaded to the renderer.
# The ordinary body() API and its native LOD are unchanged.
static var explicit_cache: Dictionary = {}

static func body_lods(size: Vector3, profile: Profile = Profile.MOLDED) -> Array[ArrayMesh]:
    var key := Vector4(size.x, size.y, size.z, float(profile))
    if explicit_cache.has(key):
        return explicit_cache[key]
    var source: Array = body(size, profile).surface_get_arrays(0)
    var levels: Array[ArrayMesh] = []
    for stride in [1, 2, 3]:
        var old_indices := PackedInt32Array()
        for face in range(6):
            _grid(old_indices, face * (STEPS + 1) * (STEPS + 1), stride)
        var vertex_indices: Dictionary = {}
        var vertices := PackedVector3Array()
        var normals := PackedVector3Array()
        var uv := PackedVector2Array()
        var indices := PackedInt32Array()
        for old in old_indices:
            if not vertex_indices.has(old):
                vertex_indices[old] = vertices.size()
                vertices.append(source[Mesh.ARRAY_VERTEX][old])
                normals.append(source[Mesh.ARRAY_NORMAL][old])
                uv.append(source[Mesh.ARRAY_TEX_UV][old])
            indices.append(int(vertex_indices[old]))
        var arrays: Array = []
        arrays.resize(Mesh.ARRAY_MAX)
        arrays[Mesh.ARRAY_VERTEX] = vertices
        arrays[Mesh.ARRAY_NORMAL] = normals
        arrays[Mesh.ARRAY_TEX_UV] = uv
        arrays[Mesh.ARRAY_INDEX] = indices
        var mesh := ArrayMesh.new()
        mesh.add_surface_from_arrays(Mesh.PRIMITIVE_TRIANGLES, arrays)
        levels.append(mesh)
    explicit_cache[key] = levels
    return levels


# Original CylinderMesh arrays at LOD0; lower tessellation of the same
# canonical primitive parameters, preserving radius/height/caps and UVs.
static var cylinder_cache: Dictionary = {}
static func cylinder_lods(source: CylinderMesh) -> Array[ArrayMesh]:
    var key := Vector4(source.top_radius,source.bottom_radius,source.height,float(source.radial_segments*100+source.rings))
    if cylinder_cache.has(key):
        return cylinder_cache[key]
    var levels: Array[ArrayMesh] = []
    for i in range(3):
        var primitive: CylinderMesh = source if i==0 else source.duplicate()
        if i>0:
            primitive.radial_segments = [source.radial_segments,24,12][i]
            primitive.rings = [source.rings,1,0][i]
        var mesh := ArrayMesh.new()
        mesh.add_surface_from_arrays(Mesh.PRIMITIVE_TRIANGLES,primitive.get_mesh_arrays())
        levels.append(mesh)
    cylinder_cache[key]=levels
    return levels
