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

def _bounds(bm):
    return tuple(tuple(fn(v.co[i] for v in bm.verts) for i in range(3))
                 for fn in (min,max))

def normalize_csg(mesh, *, evaluated=False):
    """Conservative CSG-only cleanup with explicit shape invariants.

    No repair of arbitrary input meshes. Only evaluated CSG may weld a
    sub-micrometre duplicate or dissolve a degenerate edge; volume and
    bounds must agree with the pre-cleanup evaluated surface.
    """
    bm=bmesh.new()
    try:
        bm.from_mesh(mesh)
        if not bm.faces:
            return {"empty":True}
        bm.normal_update()
        before_counts=(len(bm.verts),len(bm.edges),len(bm.faces))
        before_bounds=_bounds(bm)
        before_volume=bm.calc_volume(signed=True)
        span=max(b-a for a,b in zip(*before_bounds))
        tolerance=min(1e-7,max(1e-10,span*1e-8))
        if evaluated:
            # Collapse coincident intersection vertices and zero-area fragments
            # in the evaluated solid, never silently modify input assets.
            bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=tolerance)
            bmesh.ops.dissolve_degenerate(bm,edges=list(bm.edges),dist=tolerance)
            bm.normal_update()
        bmesh.ops.dissolve_limit(bm,angle_limit=1e-6,
            verts=list(bm.verts),edges=list(bm.edges),
            use_dissolve_boundaries=True)
        bm.normal_update()
        if evaluated:
            # Tessellate actual polygons rather than accepting the implicit
            # loop-triangle tessellation of a polygon with a collinear corner.
            bmesh.ops.triangulate(bm,faces=list(bm.faces),
                                 quad_method="BEAUTY",ngon_method="BEAUTY")
            bmesh.ops.dissolve_degenerate(bm,edges=list(bm.edges),dist=tolerance)
            bmesh.ops.triangulate(bm,faces=[f for f in bm.faces if len(f.verts)>3],
                                 quad_method="BEAUTY",ngon_method="BEAUTY")
            bm.normal_update()
        invalid=[f for f in bm.faces if not math.isfinite(f.calc_area()) or f.calc_area()<=5e-13]
        if invalid:
            detail=[[tuple(v.co) for v in f.verts] for f in invalid[:3]]
            raise ValueError("degenerate CSG polygons after normalization: "+repr(detail))
        if not bm.faces or any(not e.is_manifold for e in bm.edges):
            raise ValueError("CSG cleanup produced open or nonmanifold surface")
        if any(not v.link_faces for v in bm.verts):
            raise ValueError("CSG cleanup produced orphan vertices")
        after_bounds=_bounds(bm)
        after_volume=bm.calc_volume(signed=True)
        if not all(math.isfinite(v) for v in (before_volume,after_volume)):
            raise ValueError("nonfinite CSG volume")
        if any(abs(a-b)>4*tolerance for u,v in zip(before_bounds,after_bounds) for a,b in zip(u,v)):
            raise ValueError("CSG cleanup changed bounds")
        if not math.isclose(before_volume,after_volume,rel_tol=1e-6,
                            abs_tol=max(1e-15,4*tolerance*span*span)):
            raise ValueError("CSG cleanup changed signed volume")
        bm.to_mesh(mesh)
        mesh.update()
        return {"before":before_counts,"after":(len(bm.verts),len(bm.edges),len(bm.faces)),
                "before_volume":before_volume,"after_volume":after_volume,
                "tolerance_m":tolerance,"evaluated":evaluated}
    finally:
        bm.free()

def main():
    src,dst=map(Path,sys.argv[sys.argv.index("--")+1:])
    data=json.loads(src.read_text(encoding="utf-8"))
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.context.scene.unit_settings.system="METRIC"
    bpy.context.scene.unit_settings.scale_length=1.0
    obj=mesh_object(data["id"],data["vertices"],data["triangles"])
    normalization=[]
    if "boolean" in data:
        operation=data["boolean"]
        other=mesh_object("qa_operand",operation["vertices"],operation["triangles"])
        # Avoid artificial triangle diagonals in planar CSG operands.
        normalization.extend((normalize_csg(obj.data),normalize_csg(other.data)))
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
            normalization.append(normalize_csg(out,evaluated=True))
        out.calc_loop_triangles()
        payload={"id":data["id"],"blender_version":bpy.app.version_string,
                 "csg_normalization":normalization,
                 "vertices":[to_canonical(v.co) for v in out.vertices],
                 "triangles":[list(t.vertices) for t in out.loop_triangles]}
        dst.write_text(json.dumps(payload,allow_nan=False),encoding="utf-8")
    finally:
        evaluated.to_mesh_clear()

if __name__=="__main__":
    main()
