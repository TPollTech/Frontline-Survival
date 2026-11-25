extends RefCounted
## Canonical geometry recipes shared by the existing character assemblers.
## No rig, animation, material, collision or parent ownership policy here.
const ModelSurface = preload("res://scripts/model_surface.gd")

static func joint(parent: Node3D, location: Vector3, label: String) -> Node3D:
    var node := Node3D.new()
    node.name = label
    node.position = location
    parent.add_child(node)
    return node

static func padded(size: Vector3) -> ArrayMesh:
    return ModelSurface.body(size, ModelSurface.Profile.PADDED)

static func capsule(radius: float, height: float, radial_segments: int, rings: int) -> CapsuleMesh:
    var shape := CapsuleMesh.new()
    shape.radius = radius
    shape.height = height
    shape.radial_segments = radial_segments
    shape.rings = rings
    return shape

static func box(size: Vector3) -> BoxMesh:
    var shape := BoxMesh.new()
    shape.size = size
    return shape

static func sleeve(axis_length: float, top_radius: float, bottom_radius: float) -> ArrayMesh:
    # Elliptical cloth sections overlap at the animated elbow and wrist.
    var profile := [0.90, 1.08, 1.00, 1.13, 1.06, 1.01, 1.09, 0.90]
    var rings := [0.0, 0.09, 0.17, 0.32, 0.51, 0.74, 0.86, 1.0]
    var surface := SurfaceTool.new()
    surface.begin(Mesh.PRIMITIVE_TRIANGLES)
    var length := axis_length + minf(top_radius, bottom_radius) * 0.7
    const SIDES := 16
    for row in range(rings.size()):
        var t: float = rings[row]
        var radius: float = lerpf(bottom_radius, top_radius, t) * profile[row]
        for side in range(SIDES):
            var angle := TAU * side / SIDES
            var fold := 1.0 + 0.045 * sin(3.0 * angle + 2.0 * t)
            var tilt := 0.012 * sin(angle + t * PI) * sin(t * PI)
            surface.add_vertex(Vector3(cos(angle) * radius * fold,
                (t - 0.5) * length + tilt, sin(angle) * radius * 0.84 * fold))
    for row in range(rings.size() - 1):
        for side in range(SIDES):
            var a := row * SIDES + side
            var b := row * SIDES + (side + 1) % SIDES
            for index in [a, b, a + SIDES, b, b + SIDES, a + SIDES]:
                surface.add_index(index)
    var last := (rings.size() - 1) * SIDES
    for side in range(1, SIDES - 1):
        for index in [0, side + 1, side, last, last + side, last + side + 1]:
            surface.add_index(index)
    surface.generate_normals()
    return surface.commit()
