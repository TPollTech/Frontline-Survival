"""Executed inside Blender only. JSON is data, never executable code."""
import json
from pathlib import Path
import sys
import bpy

def to_native(v):
    x,y,z=v
    return (x,-z,y)

def to_canonical(v):
    x,y,z=v
    return (x,z,-y)

def main():
    src,dst=map(Path,sys.argv[sys.argv.index("--")+1:])
    data=json.loads(src.read_text(encoding="utf-8"))
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.context.scene.unit_settings.system="METRIC"
    bpy.context.scene.unit_settings.scale_length=1.0
    mesh=bpy.data.meshes.new(data["id"])
    mesh.from_pydata([to_native(v) for v in data["vertices"]],[],data["triangles"])
    if mesh.validate(verbose=False):
        raise ValueError("Blender repaired invalid input instead of preserving it")
    mesh.update()
    obj=bpy.data.objects.new(data["id"],mesh)
    bpy.context.collection.objects.link(obj)
    if data["bevel_m"]>0:
        mod=obj.modifiers.new("technical_bevel","BEVEL")
        mod.width=data["bevel_m"]
        mod.segments=data["segments"]
        mod.limit_method="ANGLE"
        mod.angle_limit=0.5235987755982988
        mod.use_clamp_overlap=True
    bpy.context.view_layer.update()
    evaluated=obj.evaluated_get(bpy.context.evaluated_depsgraph_get())
    out=evaluated.to_mesh()
    try:
        out.calc_loop_triangles()
        payload={"id":data["id"],"blender_version":bpy.app.version_string,
                 "vertices":[to_canonical(v.co) for v in out.vertices],
                 "triangles":[list(t.vertices) for t in out.loop_triangles]}
        dst.write_text(json.dumps(payload,allow_nan=False),encoding="utf-8")
    finally:
        evaluated.to_mesh_clear()

if __name__=="__main__":
    main()
