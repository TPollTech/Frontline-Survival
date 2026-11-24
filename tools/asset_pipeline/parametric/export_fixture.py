"""Neutral textured, skinned panel; reproducible fixture, never production asset."""
from pathlib import Path
import sys
from .model import MeshSpec,SceneSpec,NodeSpec,Transform
from .pbr import generate_library
from .rig import RigSpec,SkeletonSpec,BoneSpec,SkinSpec,SocketSpec
from .shading import build_render_mesh,planar_uv
from .exporter import source_manifest,export_bundle,write_bundle

def fixture():
    m=MeshSpec("panel",((0,0,0),(1,0,0),(1,2,0),(0,2,0)),((0,1,2),(0,2,3)))
    lib=generate_library(32)
    material=lib.material("rubber")
    scene=SceneSpec("export_fixture",(m,),(material,),(NodeSpec("anchor"),NodeSpec("panel",m.id,"anchor",material.id)))
    sk=SkeletonSpec("skeleton",(BoneSpec("root",length_m=1),BoneSpec("tip","root",Transform.translation((0,1,0)),1)))
    skin=SkinSpec(m.id,sk.id,((("root",1),),(("root",1),),(("tip",1),),(("tip",1),)))
    rig=RigSpec("rig",scene,sk,"anchor",(skin,),(SocketSpec("tip_socket","tip","bone"),))
    render=build_render_mesh(m,uv=planar_uv(m,u_axis=(1,0,0),v_axis=(0,1,0)))
    return scene,(render,),lib,rig

def main():
    scene,renders,lib,rig=fixture()
    root=Path(__file__).resolve().parents[3]
    sources=source_manifest(root,[str(p.relative_to(root)) for p in Path(__file__).parent.glob("*.py")],sys.argv[2])
    write_bundle(sys.argv[1],export_bundle(scene,renders,lib,sources=sources,rig=rig))
if __name__=="__main__":
    main()
