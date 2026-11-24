"""Run inside Blender: compute actual MikkTSpace tangents on authored corner UVs/normals."""
import json
import sys
from pathlib import Path
import bpy

def native(v):
    x,y,z=v
    return (x,-z,y)

def canonical(v):
    x,y,z=v
    return (x,z,-y)

def main():
    src,dst=map(Path,sys.argv[sys.argv.index("--")+1:])
    data=json.loads(src.read_text(encoding="utf-8"))
    bpy.ops.wm.read_factory_settings(use_empty=True)
    mesh=bpy.data.meshes.new("shading_fixture")
    mesh.from_pydata([native(v) for v in data["vertices"]],[],data["triangles"])
    if mesh.validate(verbose=False):
        raise ValueError("invalid Blender input")
    mesh.update()
    uv=mesh.uv_layers.new(name="UV0")
    order=[]
    for face,poly in zip(data["triangles"],mesh.polygons):
        if tuple(poly.vertices)!=tuple(face):
            raise ValueError("Blender changed face ordering")
        poly.use_smooth=True
        order.extend(poly.loop_indices)
    if order!=list(range(len(data["uv"]))) or len(mesh.polygons)!=len(data["triangles"]):
        raise ValueError("corner order mismatch")
    for i,p in enumerate(data["uv"]):
        uv.data[i].uv=p
    if hasattr(mesh,"use_auto_smooth"):
        mesh.use_auto_smooth=True
    mesh.normals_split_custom_set([native(n) for n in data["normals"]])
    mesh.calc_tangents(uvmap=uv.name)
    result={"version":bpy.app.version_string,
            "normals":[canonical(loop.normal) for loop in mesh.loops],
            "tangents":[canonical(loop.tangent)+(loop.bitangent_sign,) for loop in mesh.loops]}
    dst.write_text(json.dumps(result,allow_nan=False),encoding="utf-8")
    mesh.free_tangents()

if __name__=="__main__":
    main()
