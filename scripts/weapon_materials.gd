extends RefCounted
## Subtle procedural metal/polymer surfaces, multiplied by glTF COLOR_0.
## Three-plane UV projection means existing GLBs need no UV unwrapping.
static var metal_material: StandardMaterial3D
static var polymer_material: StandardMaterial3D

static func _build_surface(polymer: bool) -> StandardMaterial3D:
    var material := StandardMaterial3D.new()
    material.vertex_color_use_as_albedo = true
    material.albedo_color = Color.WHITE
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
        polymer_material = _build_surface(true)
    _paint_recursive(root)

static func _paint_recursive(node: Node) -> void:
    if node is MeshInstance3D:
        var part := node as MeshInstance3D
        var name_lower := part.name.to_lower()
        # Grouped viewmodel magazines/grips read differently from metal.
        var polymer := name_lower.contains("mag") or name_lower.contains("grip") \
            or name_lower.contains("polymer") or name_lower.contains("stock")
        part.material_override = polymer_material if polymer else metal_material
        part.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_ON
    for child in node.get_children():
        _paint_recursive(child)
