extends RefCounted
## Imported trimesh GLBs store weapon palette in glTF COLOR_0 (vertex colors).
## Godot 4 does not always use COLOR_0 with the imported default material.
## Explicitly enable vertex colors on all meshes, without overexposing white.
##
## Apply this to player viewmodels, enemies and allies.
static func apply_colors(root: Node) -> void:
    var material := StandardMaterial3D.new()
    material.vertex_color_use_as_albedo = true
    material.albedo_color = Color(1.0, 1.0, 1.0, 1.0)
    material.metallic = 0.10
    material.roughness = 0.76
    material.cull_mode = BaseMaterial3D.CULL_BACK
    _paint_recursive(root, material)

static func _paint_recursive(node: Node, material: StandardMaterial3D) -> void:
    if node is MeshInstance3D:
        var surface := node as MeshInstance3D
        surface.material_override = material
        surface.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_ON
    for child in node.get_children():
        _paint_recursive(child, material)
