extends RefCounted

static var templates: Dictionary
static var meshes: Dictionary

static func mesh(profile: String, axis_length: float = 0.0) -> ArrayMesh:
    if templates.is_empty():
        templates = JSON.parse_string(FileAccess.get_file_as_string("res://assets/models/fps_hand_templates.json"))
    var key := "%s:%.8f" % [profile, axis_length]
    if meshes.has(key):
        return meshes[key]

    var recipe: Array = templates[profile]
    var builder := SurfaceTool.new()
    builder.begin(Mesh.PRIMITIVE_TRIANGLES)
    for row: Array in recipe[0]:
        builder.add_vertex(Vector3(row[0], row[1] + axis_length * row[3], row[2]))
    for face: Array in recipe[1]:
        # OrganicLoft uses counterclockwise faces; Godot uses clockwise faces.
        builder.add_index(face[0])
        builder.add_index(face[2])
        builder.add_index(face[1])
    builder.generate_normals()
    var result := builder.commit()
    meshes[key] = result
    return result
