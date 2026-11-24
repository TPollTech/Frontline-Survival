extends SceneTree
## Read-only direct importer for the files named in the static report.
func _initialize() -> void:
    call_deferred("_run")

func _meshes(node: Node, result: Array[MeshInstance3D]) -> void:
    if node is MeshInstance3D and node.mesh != null:
        result.append(node)
    for child in node.get_children():
        _meshes(child,result)

func _run() -> void:
    var input := OS.get_environment("FRONTLINE_VALIDATION_REPORT")
    var output := OS.get_environment("FRONTLINE_IMPORT_REPORT")
    var data: Variant = JSON.parse_string(FileAccess.get_file_as_string(input))
    if not data is Dictionary or output.is_empty():
        push_error("IMPORT_VALIDATION_FAIL missing inputs")
        quit(1)
        return
    var rows: Array[Dictionary] = []
    var failures := 0
    for entry in data.files:
        var path := "res://" + str(entry.path)
        var document := GLTFDocument.new()
        var state := GLTFState.new()
        var code := document.append_from_file(path,state)
        var row := {"path":entry.path,"sha256":FileAccess.get_sha256(path),"import_code":code,"mesh_nodes":0,"triangles":0,"unknown_topology":0,"visual_approval":false}
        if code == OK:
            var scene := document.generate_scene(state)
            if scene != null:
                root.add_child(scene)
                var meshes: Array[MeshInstance3D] = []
                _meshes(scene,meshes)
                row["mesh_nodes"]=meshes.size()
                for mesh in meshes:
                    for i in range(mesh.mesh.get_surface_count()):
                        var arrays := mesh.mesh.surface_get_arrays(i)
                        if not mesh.mesh is ArrayMesh or (mesh.mesh as ArrayMesh).surface_get_primitive_type(i)!=Mesh.PRIMITIVE_TRIANGLES:
                            row["unknown_topology"]+=1
                            continue
                        var count: int = 0
                        if arrays[Mesh.ARRAY_INDEX]!=null and arrays[Mesh.ARRAY_INDEX].size()>0:
                            count=arrays[Mesh.ARRAY_INDEX].size()
                        elif arrays[Mesh.ARRAY_VERTEX]!=null:
                            count=arrays[Mesh.ARRAY_VERTEX].size()
                        row["triangles"]+=int(count/3.0)
                scene.free()
            else:
                row["import_code"]=FAILED
        if row["import_code"]!=OK or row["mesh_nodes"]==0:
            failures+=1
        rows.append(row)
        print("IMPORT_VALIDATION_FILE ",JSON.stringify(row))
    var report := FileAccess.open(output,FileAccess.WRITE)
    if report==null:
        quit(1)
        return
    report.store_string(JSON.stringify({"revision":data.get("revision"),"engine":Engine.get_version_info(),"files":rows,"failures":failures,"visual_approval":false}))
    report.close()
    print("IMPORT_VALIDATION_COMPLETE ",rows.size()," failures=",failures)
    quit(0 if failures==0 else 1)
