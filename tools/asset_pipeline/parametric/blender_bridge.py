"""Executed inside Blender only. JSON is data, never executable code."""
import json
from pathlib import Path
import sys
import bpy
import bmesh
import math

def to_native(v):
    x,y,z=v
    return (x,-z,y)

def to_canonical(v):
    x,y,z=v
    return (x,z,-y)

def mesh_object(name, vertices, triangles):
    mesh=bpy.data.meshes.new(name)
    mesh.from_pydata([to_native(v) for v in vertices],[],triangles)
    if mesh.validate(verbose=False):
        raise ValueError("Blender repaired invalid input instead of preserving it")
    mesh.update()
    obj=bpy.data.objects.new(name,mesh)
    bpy.context.collection.objects.link(obj)
    return obj

def normalize_csg(mesh):
    """Remove redundant coplanar partitions; keep actual solid boundaries.
    Do not use this on plain roundtrip or bevel results.
    """
    bm=bmesh.new()
    try:
        bm.from_mesh(mesh)
        if not bm.faces:
            return
        bm.normal_update()
        # Dissolve only coplanar edges and redundant collinear vertices.
        # No merge-by-distance: nearby independent features must survive.
        bmesh.ops.dissolve_limit(bm,angle_limit=1e-6,
            verts=list(bm.verts),edges=list(bm.edges),
            use_dissolve_boundaries=False)
        bm.normal_update()
        if any(not f.is_valid or not math.isfinite(f.calc_area()) or f.calc_area()<=0
               for f in bm.faces):
            raise ValueError("invalid CSG polygon after coplanar dissolve")
        bm.to_mesh(mesh)
        mesh.update()
    finally:
        bm.free()

def main():
    src,dst=map(Path,sys.argv[sys.argv.index("--")+1:])
    data=json.loads(src.read_text(encoding="utf-8"))
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.context.scene.unit_settings.system="METRIC"
    bpy.context.scene.unit_settings.scale_length=1.0
    obj=mesh_object(data["id"],data["vertices"],data["triangles"])
    if "boolean" in data:
        operation=data["boolean"]
        other=mesh_object("qa_operand",operation["vertices"],operation["triangles"])
        # Avoid artificial triangle diagonals in planar CSG operands.
        normalize_csg(obj.data)
        normalize_csg(other.data)
        mod=obj.modifiers.new("exact_csg","BOOLEAN")
        # Public recipe names are not identical to bpy enum identifiers.
        mod.operation={"union":"UNION","difference":"DIFFERENCE",
                       "intersection":"INTERSECT"}[operation["operation"]]
        mod.solver="EXACT"
        mod.object=other
    if data["bevel_m"]>0:
        mod=obj.modifiers.new("technical_bevel","BEVEL")
        mod.width=data["bevel_m"]
        mod.segments=data["segments"]
        mod.limit_method="ANGLE"
        mod.angle_limit=data.get("angle_rad",0.5235987755982988)
        mod.use_clamp_overlap=True
    bpy.context.view_layer.update()
    evaluated=obj.evaluated_get(bpy.context.evaluated_depsgraph_get())
    out=evaluated.to_mesh()
    try:
        if "boolean" in data:
            normalize_csg(out)
        out.calc_loop_triangles()
        payload={"id":data["id"],"blender_version":bpy.app.version_string,
                 "vertices":[to_canonical(v.co) for v in out.vertices],
                 "triangles":[list(t.vertices) for t in out.loop_triangles]}
        dst.write_text(json.dumps(payload,allow_nan=False),encoding="utf-8")
    finally:
        evaluated.to_mesh_clear()

if __name__=="__main__":
    main()
