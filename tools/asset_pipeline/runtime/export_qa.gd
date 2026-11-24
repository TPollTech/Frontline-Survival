extends SceneTree
func _initialize() -> void:
    call_deferred("_run")

func _run() -> void:
    for path in ["res://asset.glb","res://asset.gltf"]:
        var doc := GLTFDocument.new()
        var state := GLTFState.new()
        if doc.append_from_file(path,state)!=OK:
            push_error("EXPORT_QA_FAIL import "+path)
            quit(1)
            return
        var scene := doc.generate_scene(state)
        if scene==null:
            push_error("EXPORT_QA_FAIL scene "+path)
            quit(1)
            return
        root.add_child(scene)
        var meshes := scene.find_children("*","MeshInstance3D",true,false)
        var skeletons := scene.find_children("*","Skeleton3D",true,false)
        if meshes.size()!=1 or skeletons.size()!=1:
            push_error("EXPORT_QA_FAIL missing mesh or skeleton "+path)
            quit(1)
            return
        var mesh: MeshInstance3D = meshes[0]
        var sk: Skeleton3D = skeletons[0]
        var arrays := mesh.mesh.surface_get_arrays(0)
        var material := mesh.mesh.surface_get_material(0) as StandardMaterial3D
        if sk.get_bone_count()!=2 or mesh.skin==null or arrays[Mesh.ARRAY_INDEX].size()!=6 or arrays[Mesh.ARRAY_TANGENT].size()!=16 or arrays[Mesh.ARRAY_TEX_UV].size()!=4 or material==null:
            push_error("EXPORT_QA_FAIL attributes "+path+" bones="+str(sk.get_bone_count())+" skin="+str(mesh.skin!=null)+" indices="+str(arrays[Mesh.ARRAY_INDEX].size())+" tangents="+str(arrays[Mesh.ARRAY_TANGENT].size())+" uv="+str(arrays[Mesh.ARRAY_TEX_UV].size())+" material="+str(material!=null))
            quit(1)
            return
        if material.albedo_texture==null or material.normal_texture==null or material.roughness_texture==null:
            push_error("EXPORT_QA_FAIL textures "+path)
            quit(1)
            return
        print("EXPORT_FORMAT_PASS ",path," bones=",sk.get_bone_count()," triangles=2 textures=true")
        scene.free()
    print("EXPORT_GODOT_PASS")
    quit(0)
