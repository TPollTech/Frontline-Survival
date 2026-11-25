extends SceneTree
## Local headless contract checks for shared world recipes; no screenshot or FPS claim.
const Geometry = preload("res://scripts/world_asset_geometry.gd")
const Surface = preload("res://scripts/model_surface.gd")
var checks := 0
var failures := 0

func _initialize() -> void:
    call_deferred("_run")

func expect(ok: bool, message: String) -> void:
    checks += 1
    if not ok:
        failures += 1
        push_error("WORLD_ASSET_GEOMETRY_FAIL " + message)

func _run() -> void:
    var solid_size := Vector3(2.5, 1.6, 4.0)
    var thin_size := Vector3(1.5, 0.025, 0.11)
    var thick_size := Vector3(2.6, 0.7, 1.8)
    var solid := Geometry.world_box(solid_size, true)
    var thin := Geometry.world_box(thin_size, false)
    var thick := Geometry.world_box(thick_size, false)
    expect(solid is BoxMesh and solid.get_aabb().size.is_equal_approx(solid_size), "solid mesh")
    expect(thin is BoxMesh and thin.get_aabb().size.is_equal_approx(thin_size), "thin decoration")
    expect(thick == Surface.body(thick_size, Surface.Profile.MACHINED), "machined mesh identity")
    expect(Geometry.machined(thick_size) == thick, "shared machined cache")
    var threshold := Vector3(1.0, 0.035, 1.0)
    expect(Geometry.world_box(threshold, false) is ArrayMesh, "thin threshold")
    var original := CylinderMesh.new()
    original.top_radius = 0.33
    original.bottom_radius = 0.42
    original.height = 0.8
    var generated := Geometry.cylinder(0.33, 0.42, 0.8)
    expect(generated.get_mesh_arrays() == original.get_mesh_arrays(), "native cylinder buffers")
    expect(generated.radial_segments == original.radial_segments and generated.rings == original.rings, "native cylinder defaults")
    expect(generated != original, "independent primitive")
    var env := Geometry.depot_environment()
    expect(env.background_mode == Environment.BG_SKY and env.sky.sky_material is ProceduralSkyMaterial, "sky")
    expect(env.fog_enabled and is_equal_approx(env.fog_density, 0.0025), "fog")
    expect(is_equal_approx(env.ambient_light_energy, 0.65), "ambient light")
    var sun := Geometry.depot_sun()
    expect(sun.shadow_enabled and is_equal_approx(sun.light_energy, 1.24), "sun")
    expect(sun.rotation_degrees.is_equal_approx(Vector3(-32, -49, 0)), "sun orientation")
    sun.free()
    print("WORLD_ASSET_GEOMETRY ", checks - failures, "/", checks, " checks")
    quit(1 if failures else 0)
