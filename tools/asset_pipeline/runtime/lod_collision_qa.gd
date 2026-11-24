extends SceneTree
# Isolated neutral fixture; not gameplay integration or visual approval.
var world: Node3D
var visual: MeshInstance3D
var body: StaticBody3D
var shape: CollisionShape3D
var meshes: Array[ArrayMesh] = []

func fail(message: String) -> void:
    push_error("LOD_COLLISION_FAIL " + message)
    quit(1)

func _initialize() -> void:
    call_deferred("_run")

func _run() -> void:
    var data = JSON.parse_string(FileAccess.get_file_as_string("res://fixture.json"))
    if not data is Dictionary:
        fail("invalid fixture")
        return
    world = Node3D.new()
    root.add_child(world)
    visual = MeshInstance3D.new()
    world.add_child(visual)
    var expected := [256,128,64]
    for level in data.asset.levels:
        var spec = level.scene.meshes[0]
        var vertices := PackedVector3Array()
        var indices := PackedInt32Array()
        for v in spec.vertices:
            vertices.append(Vector3(v[0],v[1],v[2]))
        # Godot front-face winding is clockwise.
        for f in spec.triangles:
            indices.append_array(PackedInt32Array([int(f[0]),int(f[2]),int(f[1])]))
        var arrays := []
        arrays.resize(Mesh.ARRAY_MAX)
        arrays[Mesh.ARRAY_VERTEX] = vertices
        arrays[Mesh.ARRAY_INDEX] = indices
        var mesh := ArrayMesh.new()
        mesh.add_surface_from_arrays(Mesh.PRIMITIVE_TRIANGLES,arrays)
        if mesh.surface_get_array_index_len(0)/3 != expected[meshes.size()]:
            fail("triangle count mismatch")
            return
        meshes.append(mesh)
    body = StaticBody3D.new()
    shape = CollisionShape3D.new()
    var box := BoxShape3D.new()
    var dimensions = data.asset.colliders[0].dimensions_m
    box.size = Vector3(dimensions[0],dimensions[1],dimensions[2])
    shape.shape = box
    body.add_child(shape)
    world.add_child(body)
    var collider_id := shape.shape.get_instance_id()
    for i in range(meshes.size()):
        visual.mesh = meshes[i]
        await physics_frame
        await physics_frame
        var query := PhysicsRayQueryParameters3D.create(Vector3(0,0,3),Vector3(0,0,-3))
        var hit := world.get_world_3d().direct_space_state.intersect_ray(query)
        if hit.is_empty() or hit.collider != body or absf(hit.position.z-0.5)>0.001:
            fail("collision ray mismatch at LOD " + str(i))
            return
        if shape.shape.get_instance_id()!=collider_id:
            fail("collider changed with LOD")
            return
        print("LOD_COLLISION_LEVEL_PASS ",i," triangles=",expected[i]," hit_z=",hit.position.z)
    print("LOD_COLLISION_GODOT_PASS")
    quit(0)
