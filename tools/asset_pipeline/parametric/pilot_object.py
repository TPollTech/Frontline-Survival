"""Canonical QA-only industrial bollard: exact same exports for Studio and Godot."""
import argparse,json,hashlib
from pathlib import Path
from .model import SceneSpec,NodeSpec,Transform
from .recipes import PythonBackend,Revolution,Box
from .shading import build_render_mesh
from .pilot_finish import finished_library,bevel_block
from .exporter import source_manifest,export_bundle,write_bundle
from .lod import BUDGETS
from tools.asset_pipeline.validate_gltf import Audit
from tools.asset_pipeline.live_catalog import canonical

# Authored dimensions in metres; ground pivot, canonical Y up.
# Industrial safety bollard, not based on a proprietary manufacturer's drawing.
PROFILE=((0,.045),(.07,.045),(.076,.055),(.076,.57),(0,.57))
TOP_PROFILE=((0,.66),(.076,.66),(.076,.76),(.073,.80),(.058,.825),(0,.835))
BAND_PROFILE=((0,.57),(.076,.57),(.082,.575),(.082,.655),(.076,.66),(0,.66))
BASE=(.22,.045,.22)
LEVELS=(48,24,12)
CONTRACT={"unit":"m","up":"+Y","dimensions_m":[.22,.835,.22],
          "pivots_local_m":{"anchor":[0,0,0],"base":[0,0,0],"body":[0,0,0],"body_top":[0,0,0],"band":[0,0,0]},
          "forward":{"node":"anchor","local_axis":[0,0,-1],"world_axis":[0,0,-1]},"tolerance_m":.001}
def build(level):
    backend=PythonBackend();n=LEVELS[level]
    meshes=(bevel_block("base",BASE,level),
            backend.build(Revolution("body",PROFILE,n)),
            backend.build(Revolution("body_top",TOP_PROFILE,n)),
            backend.build(Revolution("band",BAND_PROFILE,n)))
    lib=finished_library(128,9133)
    names=sorted(m.id for m in lib.materials)
    # Reuse existing authored material presets; no custom renderer materials.
    metal="safety_amber"
    rubber="graphite"
    mats=tuple(lib.material(m) for m in sorted({metal,rubber}))
    nodes=(NodeSpec("anchor"),NodeSpec("base","base","anchor",metal,Transform.translation((0,0,0))),
           NodeSpec("body","body","anchor",metal),NodeSpec("body_top","body_top","anchor",metal),NodeSpec("band","band","anchor",rubber))
    scene=SceneSpec("pilot_bollard",meshes,mats,nodes)
    return scene,tuple(build_render_mesh(m) for m in meshes),lib

def main():
    p=argparse.ArgumentParser();p.add_argument("output");p.add_argument("revision");a=p.parse_args()
    out=Path(a.output);out.mkdir(parents=True,exist_ok=True)
    root=Path(__file__).resolve().parents[3]
    sources=source_manifest(root,[p.relative_to(root).as_posix() for p in Path(__file__).parent.glob("*.py")],a.revision)
    rows=[]
    for level in range(3):
        scene,renders,lib=build(level)
        folder=out/f"lod{level}";write_bundle(folder,export_bundle(scene,renders,lib,sources=sources))
        for name in ("asset.glb","asset.gltf"):
            result=Audit(folder,name,"object",True,root,CONTRACT).run()
            if result["errors"]:raise ValueError(result)
            result["level"]=level;rows.append(result)
        if rows[-1]["metrics"]["triangles"]>BUDGETS["object"].triangles[level]:raise ValueError("LOD budget exceeded")
    tris=[r["metrics"]["triangles"] for r in rows if r["path"]=="asset.glb"]
    if not tris[0]>tris[1]>tris[2]:raise ValueError("LOD counts must decrease")
    result={"id":"qa:industrial_bollard","category":"object","revision":a.revision,"contract":CONTRACT,
        "reference":"generic industrial ground-mounted bollard; authored concept, no claimed replica",
        "source":"tools/asset_pipeline/parametric/pilot_object.py","exports":rows,
        "collision":{"type":"box","size_m":[.22,.835,.22],"center_m":[0,.4175,0],"independent":True},
        "lod_distances_m":[0,15,35],"budget_scope":"one assembled instance, provisional",
        "visual_approval":False,"production_integrated":False}
    (out/"pilot-report.json").write_bytes(canonical(result))
    print("PILOT_EXPORT_PASS",tris)
if __name__=="__main__":main()
