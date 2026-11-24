"""Actual Blender armature and evaluated skin for neutral validation fixtures."""
import bpy
import json
import sys
from pathlib import Path
from mathutils import Matrix

C=Matrix(((1,0,0,0),(0,0,-1,0),(0,1,0,0),(0,0,0,1)))
def matrix(values):
    return Matrix(tuple(tuple(values[c*4+r] for c in range(4)) for r in range(4)))

def main():
    src,dst=map(Path,sys.argv[sys.argv.index("--")+1:])
    d=json.loads(src.read_text())
    bpy.ops.wm.read_factory_settings(use_empty=True)
    arm=bpy.data.armatures.new("fixture_skeleton")
    obj=bpy.data.objects.new("fixture_armature",arm)
    bpy.context.collection.objects.link(obj)
    bpy.context.view_layer.objects.active=obj
    obj.select_set(True)
    bpy.ops.object.mode_set(mode="EDIT")
    for spec in d["bones"]:
        bone=arm.edit_bones.new(spec["id"])
        if spec["parent_id"]:
            bone.parent=arm.edit_bones[spec["parent_id"]]
        bone.matrix=C@matrix(spec["rest_world"])
        bone.length=spec["length_m"]
    bpy.ops.object.mode_set(mode="OBJECT")
    # Local +Y is bone longitudinal axis in both representations. C maps
    # armature-space only; pose delta is expressed in bone-local axes.
    for spec in d["bones"]:
        obj.pose.bones[spec["id"]].matrix_basis=matrix(spec["delta"])
    mesh=bpy.data.meshes.new("fixture_mesh")
    mesh.from_pydata([tuple(C.to_3x3()@__import__("mathutils").Vector(p)) for p in d["vertices"]],[],d["triangles"])
    mesh.update()
    skin=bpy.data.objects.new("fixture_skin",mesh)
    bpy.context.collection.objects.link(skin)
    groups={b["id"]:skin.vertex_groups.new(name=b["id"]) for b in d["bones"]}
    for i,row in enumerate(d["weights"]):
        for bone,w in row:
            groups[bone].add([i],w,"REPLACE")
    mod=skin.modifiers.new("linear_skin","ARMATURE")
    mod.object=obj
    mod.use_deform_preserve_volume=False
    bpy.context.view_layer.update()
    evaluated=skin.evaluated_get(bpy.context.evaluated_depsgraph_get())
    result=evaluated.to_mesh()
    try:
        inv=C.inverted()
        vertices=[tuple(inv.to_3x3()@v.co) for v in result.vertices]
        def flat(m):
            return [m[r][c] for c in range(4) for r in range(4)]
        dst.write_text(json.dumps({"version":bpy.app.version_string,"vertices":vertices,
            "pose_world":{b.name:flat(inv@b.matrix) for b in obj.pose.bones}},allow_nan=False))
    finally:
        evaluated.to_mesh_clear()

if __name__=="__main__":
    main()
