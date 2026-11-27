extends RefCounted
## Canonical visual recipes for world assets; gameplay retains node ownership,
## transforms, material overrides, collision shapes, interactions and LOD policy.
const ModelSurface = preload("res://scripts/model_surface.gd")

static func box(size: Vector3) -> BoxMesh:
    var mesh := BoxMesh.new()
    mesh.size = size
    return mesh

static func machined(size: Vector3) -> ArrayMesh:
    return ModelSurface.body(size, ModelSurface.Profile.MACHINED)

static func world_box(size: Vector3, solid: bool) -> Mesh:
    # Preserve the legacy thin-decoration threshold and solid box silhouette.
    if solid or size[size.min_axis_index()] < 0.035:
        return box(size)
    return machined(size)

static func cylinder(top_radius: float, bottom_radius: float, height: float) -> CylinderMesh:
    var mesh := CylinderMesh.new()
    mesh.top_radius = top_radius
    mesh.bottom_radius = bottom_radius
    mesh.height = height
    return mesh

static func depot_environment() -> Environment:
    var environment := Environment.new()
    environment.background_mode = Environment.BG_SKY
    var sky := Sky.new()
    var sky_mat := ProceduralSkyMaterial.new()
    sky_mat.sky_top_color = Color(0.25, 0.38, 0.49)
    sky_mat.sky_horizon_color = Color(0.78, 0.76, 0.70)
    sky_mat.ground_bottom_color = Color(0.17, 0.20, 0.19)
    sky.sky_material = sky_mat
    environment.sky = sky
    environment.ambient_light_source = Environment.AMBIENT_SOURCE_SKY
    environment.ambient_light_energy = 0.65
    environment.fog_enabled = true
    environment.fog_light_color = Color(0.64, 0.68, 0.69)
    environment.fog_density = 0.0025
    return environment

static func depot_sun() -> DirectionalLight3D:
    var sun := DirectionalLight3D.new()
    sun.rotation_degrees = Vector3(-32, -49, 0)
    sun.light_color = Color(1.0, 0.90, 0.77)
    sun.light_energy = 1.24
    sun.shadow_enabled = true
    return sun
