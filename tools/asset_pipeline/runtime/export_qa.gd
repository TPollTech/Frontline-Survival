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
        if mesh.skin==null or arrays[Mesh.ARRAY_INDEX].size()!=6 or arrays[Mesh.ARRAY_TANGENT].size()!=16 or arrays[Mesh.ARRAY_TEX_UV].size()!=4 or material==null:
            push_error("EXPORT_QA_FAIL attributes "+path+" bones="+str(sk.get_bone_count())+" skin="+str(mesh.skin!=null)+" indices="+str(arrays[Mesh.ARRAY_INDEX].size())+" tangents="+str(arrays[Mesh.ARRAY_TANGENT].size())+" uv="+str(arrays[Mesh.ARRAY_TEX_UV].size())+" material="+str(material!=null))
            quit(1)
            return
        # Godot may promote a non-joint child of a joint (a locator/socket)
        # into an unweighted helper bone. Validate the authored joints, the
        # helper identity and hierarchy, and the actual bind/weight mappings.
        var authored := {}
        var names: Array[String] = []
        for i in range(sk.get_bone_count()):
            var name := String(sk.get_bone_name(i))
            names.append(name)
            var key := name.to_lower().replace(":","").replace("_","").replace("/","").replace(" ","")
            authored[key]=i
        var root_bone: int = authored.get("boneroot",-1)
        var tip_bone: int = authored.get("bonetip",-1)
        var socket_bone: int = authored.get("sockettipsocket",-1)
        print("EXPORT_RIG_DIAGNOSTICS ",path," bones=",names," binds=",mesh.skin.get_bind_count()," weights=",arrays[Mesh.ARRAY_WEIGHTS].size())
        if sk.get_bone_count()!=3 or root_bone<0 or tip_bone<0 or socket_bone<0:
            push_error("EXPORT_QA_FAIL unexpected rig nodes "+path+" "+str(names))
            quit(1)
            return
        if sk.get_bone_parent(root_bone)!=-1 or sk.get_bone_parent(tip_bone)!=root_bone or sk.get_bone_parent(socket_bone)!=tip_bone or not sk.get_bone_rest(tip_bone).origin.is_equal_approx(Vector3(0,1,0)) or not sk.get_bone_rest(socket_bone).origin.is_zero_approx():
            push_error("EXPORT_QA_FAIL rig hierarchy/rest "+path)
            quit(1)
            return
        var bone_indices: PackedInt32Array = arrays[Mesh.ARRAY_BONES]
        var weights: PackedFloat32Array = arrays[Mesh.ARRAY_WEIGHTS]
        if bone_indices.size()!=16 or weights.size()!=16:
            push_error("EXPORT_QA_FAIL skin attribute length "+path)
            quit(1)
            return
        var influenced := {}
        for i in range(weights.size()):
            if weights[i]<=0.000001:
                continue
            var bind_index := bone_indices[i]
            if bind_index<0 or bind_index>=mesh.skin.get_bind_count():
                push_error("EXPORT_QA_FAIL invalid skin bind "+path)
                quit(1)
                return
            var bone := mesh.skin.get_bind_bone(bind_index)
            if mesh.skin.get_bind_name(bind_index)!=&"":
                bone=sk.find_bone(mesh.skin.get_bind_name(bind_index))
            if bone!=root_bone and bone!=tip_bone:
                push_error("EXPORT_QA_FAIL weight on unexpected helper "+path)
                quit(1)
                return
            influenced[bone]=true
        if influenced.size()!=2:
            push_error("EXPORT_QA_FAIL missing authored joint weights "+path)
            quit(1)
            return
        if material.albedo_texture==null or material.normal_texture==null or material.roughness_texture==null:
            push_error("EXPORT_QA_FAIL textures "+path)
            quit(1)
            return
        print("EXPORT_FORMAT_PASS ",path," authored_joints=2 socket_helpers=1 triangles=2 textures=true")
        scene.free()
    print("EXPORT_GODOT_PASS")
    quit(0)
