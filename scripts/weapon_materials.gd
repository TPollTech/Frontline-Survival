extends RefCounted
## Subtle procedural metal/polymer surfaces, multiplied by glTF COLOR_0.
## Three-plane UV projection means existing GLBs need no UV unwrapping.
const PROFILES := {
    "painted_metal": false, "exposed_metal": false, "brass": false,
    "polymer": true, "rubber": true, "wood": true,
}
static var profiled_materials: Dictionary = {}
static var metal_material: StandardMaterial3D

static func _build_surface(polymer: bool) -> StandardMaterial3D:
    var material := StandardMaterial3D.new()
    material.vertex_color_use_as_albedo = true
    material.albedo_color = Color.WHITE
    # Original meshes are opaque; only explicitly authored optics/effects use alpha.
    material.transparency = BaseMaterial3D.TRANSPARENCY_DISABLED
    material.albedo_texture = load(
        "res://assets/textures/weapon_polymer_albedo.png"
        if polymer else "res://assets/textures/weapon_metal_albedo.png"
    )
    material.normal_enabled = true
    material.normal_texture = load(
        "res://assets/textures/weapon_polymer_normal.png"
        if polymer else "res://assets/textures/weapon_metal_normal.png"
    )
    material.normal_scale = 0.24 if polymer else 0.38
    material.metallic = 0.06 if polymer else 0.48
    material.roughness = 0.86 if polymer else 0.59
    material.uv1_triplanar = true
    material.uv1_scale = Vector3.ONE * (4.0 if polymer else 8.0)
    material.cull_mode = BaseMaterial3D.CULL_BACK
    return material

static func apply_colors(root: Node) -> void:
    if metal_material == null:
        metal_material = _build_surface(false)
    _paint_recursive(root)

static func _paint_recursive(node: Node) -> void:
    if node is MeshInstance3D:
        var part := node as MeshInstance3D
        if part.mesh != null:
            for i in range(part.mesh.get_surface_count()):
                var source := part.mesh.surface_get_material(i) as StandardMaterial3D
                if source != null and PROFILES.has(source.resource_name):
                    if not profiled_materials.has(source):
                        var material := _build_surface(PROFILES[source.resource_name])
                        material.resource_name = source.resource_name
                        var texture_path := "res://assets/textures/weapon_surfaces/" + source.resource_name
                        material.albedo_texture = load(texture_path + "_base_color.png")
                        material.normal_texture = load(texture_path + "_normal.png")
                        var orm := load(texture_path + "_orm.png") as Texture2D
                        # ORM contains absolute factors in G and B.
                        material.roughness = 1.0
                        material.metallic = 1.0
                        material.roughness_texture = orm
                        material.metallic_texture = orm
                        material.roughness_texture_channel = BaseMaterial3D.TEXTURE_CHANNEL_GREEN
                        material.metallic_texture_channel = BaseMaterial3D.TEXTURE_CHANNEL_BLUE
                        if source.resource_name == "wood":
                            material.uv1_scale = Vector3(5.0, 5.0, 2.0)
                        profiled_materials[source] = material
                    part.set_surface_override_material(i, profiled_materials[source])
                elif source == null or source.vertex_color_use_as_albedo:
                    part.set_surface_override_material(i, metal_material)
        part.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_ON
    for child in node.get_children():
        _paint_recursive(child)
