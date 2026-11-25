"""Authorial QA-only visual pilots. No gameplay behavior or production replacements."""
import argparse
from pathlib import Path
from .model import SceneSpec,NodeSpec,Transform
from .recipes import PythonBackend,Extrusion
from .organic import OrganicLoft,LoftSection
from .shading import build_render_mesh
from .pilot_finish import bevel_block,finished_library
from .pilot_art import ART_NAMES,detailed
from .pilot_anatomy import RIG_NAMES,shape,make_rig
from .blender_backend import BlenderBackend
import subprocess
from .exporter import source_manifest,export_bundle,write_bundle
from .lod import BUDGETS
from tools.asset_pipeline.validate_gltf import Audit
from tools.asset_pipeline.live_catalog import canonical

# Each part specifies authored physical envelope and bottom-center local pivot.
# Stylized QA concepts, not manufacturer replicas or production-ready designs.
def part(id,kind,center,size,material):
    return {"id":id,"kind":kind,"center":center,"size":size,"material":material}

P=part
PILOTS={
 "training_prop":("weapon",[
 P("shell","chamfer",(0,.15,0),(.085,.13,.58),"painted_steel"),
 P("fore_shell","chamfer",(0,.15,-.32),(.065,.085,.19),"rubber"),
 P("rear_pad","chamfer",(0,.14,.32),(.09,.14,.10),"rubber"),
 P("grip_shape","loft",(0,.065,.08),(.065,.13,.08),"rubber"),
 P("top_shell","chamfer",(0,.226,0),(.045,.025,.20),"brushed_metal")],
 "fictional solid training prop silhouette; no internal or functional weapon mechanisms"),
 "optic_shell":("accessory",[
 P("mount_shell","chamfer",(0,.014,0),(.045,.028,.10),"painted_steel"),
 P("housing","loft",(0,.052,0),(.065,.065,.105),"rubber"),
 P("top_trim","chamfer",(0,.087,0),(.044,.012,.055),"brushed_metal")],
 "opaque fictional optical accessory housing; no optical function"),
 "glove":("first_person",[
 P("cuff","loft",(0,.028,0),(.075,.056,.041),"fabric"),
 P("palm","loft",(0,.078,0),(.096,.092,.045),"fabric"),
 *[P("finger_"+str(i),"loft",(x,.105+h/2,0),(.018,h,.021),"rubber") for i,(x,h) in enumerate([(-.032,.058),(-.011,.076),(.011,.071),(.032,.052)])],
 P("thumb","loft",(-.042,.088,.010),(.032,.064,.031),"rubber")],
 "glove anatomy study with finger-chain skeleton and blended weights; separate material shells"),
 "mannequin":("character",[
 P("torso","loft",(0,1.185,0),(.48,.69,.25),"fabric"),
 P("head","loft",(0,1.61,0),(.235,.32,.24),"rubber"),
 *[P("leg_"+str(i),"loft",(x,.45,0),(.16,.83,.16),"fabric") for i,x in enumerate([-.11,.11])],
 *[P("arm_"+str(i),"loft",(x,1.15,0),(.155,.65,.16),"fabric") for i,x in enumerate([-.225,.225])],
 *[P("boot_"+str(i),"chamfer",(x,.065,-.045),(.17,.13,.30),"rubber") for i,x in enumerate([-.11,.11])]],
 "clothed mannequin with arm and leg chains, blended weights and rest pose; not a production character"),
 "shelter":("structure",[
 P("slab","chamfer",(0,.10,0),(2.8,.20,2.2),"concrete"),
 *[P("post_"+str(i),"loft",(x,1.30,z),(.18,2.2,.18),"painted_steel") for i,(x,z) in enumerate([(-1.2,-.9),(1.2,-.9),(-1.2,.9),(1.2,.9)])],
 P("roof","chamfer",(0,2.45,0),(2.8,.18,2.2),"painted_steel"),
 P("back","chamfer",(0,1.25,.92),(2.25,1.8,.12),"painted_steel")],
 "open-front industrial shelter; visual geometry, no gameplay collision or navigation"),
 "supply_station":("object",[
 P("plinth","chamfer",(0,.09,0),(1.1,.18,.65),"concrete"),
 P("cabinet","chamfer",(0,.65,0),(.88,.98,.52),"painted_steel"),
 P("console","chamfer",(0,1.23,-.04),(1.0,.20,.58),"rubber"),
 P("knob","loft",(.31,1.36,-.08),(.08,.06,.08),"brushed_metal")],
 "industrial supply kiosk concept; no purchase logic"),
 "planter":("environment",[
 P("base","chamfer",(0,.18,0),(1.0,.36,.72),"concrete"),
 P("soil","chamfer",(0,.35,0),(.82,.08,.56),"wood"),
 *[P("plant_"+str(i),"loft",(x,.55,z),(.27,.48,.25),"fabric") for i,(x,z) in enumerate([(-.25,-.10),(.22,-.08),(0,.16)])]],
 "planter with simplified organic foliage masses, not botanical simulation"),
 "terrain_tile":("terrain",[
 P("ground","chamfer",(0,.10,0),(4,.2,4),"concrete"),
 P("ridge_a","loft",(-.9,.24,.5),(2.2,.28,1.7),"concrete"),
 P("ridge_b","loft",(1.0,.18,-.8),(1.6,.20,1.8),"concrete")],
 "terrain chunk study with authored raised surfaces; no navigation bake"),
 "yard_composition":("map",[
 P("ground","chamfer",(0,.10,0),(6,.2,5),"concrete"),
 P("wall","chamfer",(0,1.2,2.25),(5.6,2.2,.25),"concrete"),
 P("crate","chamfer",(-1.5,.55,-.6),(.9,.7,.8),"wood"),
 P("cabinet","chamfer",(1.3,.75,.8),(.8,1.1,.55),"painted_steel"),
 P("post_a","loft",(-2.1,.58,-1.7),(.18,.76,.18),"painted_steel"),
 P("post_b","loft",(2.1,.58,-1.7),(.18,.76,.18),"painted_steel")],
 "authored multi-object yard chunk; not an export of the existing map or a complete playable map"),
}
# Four additional geometry categories. Collision visual is explicitly a QA proxy
# for a dedicated authored box shape, not a claim about legacy gameplay physics.
PILOTS.update({
 "utility_cart":("vehicle",[
 P("deck","chamfer",(0,.40,0),(1.25,.18,1.8),"cool_steel"),
 P("cab","chamfer",(0,.88,-.35),(.96,.75,.72),"safety_amber"),
 P("cargo","chamfer",(0,.64,.48),(1.10,.48,.75),"graphite"),
 *[P("wheel_"+str(i),"loft",(x,.23,z),(.22,.46,.46),"graphite") for i,(x,z) in enumerate([(-.63,-.60),(.63,-.60),(-.63,.60),(.63,.60)])]],
 "static industrial utility cart; visual only, no drive or wheel physics"),
 "signal_effect":("effect",[
 P("signal_volume","loft",(0,.15,0),(.16,.30,.16),"signal_lime")],
 "opaque static signal-volume geometry study, not a particle or shader effect"),
 "collision_proxy":("collision",[
 P("proxy","box",(0,.50,0),(.60,1.0,.60),"signal_blue")],
 "visual QA representation of the authored independent box; Godot Shape3D verified separately"),
 "geometry_sample":("geometry_library",[
 P("profile","chamfer",(-.45,.30,0),(.60,.60,.60),"cool_steel"),
 P("loft_sample","loft",(.45,.45,0),(.65,.90,.65),"safety_amber")],
 "authored chamfer and loft demonstration using the canonical geometry library"),
})
SEGMENTS=(48,24,8)
# Palette refinements are local to QA. No edits to production material library.
PALETTE={
 "training_prop":{"shell":"cool_steel","fore_shell":"graphite","rear_pad":"graphite","top_shell":"brushed_metal"},
 "optic_shell":{"housing":"graphite","mount_shell":"cool_steel","top_trim":"signal_blue"},
 "glove":{"cuff":"olive_textile","palm":"olive_textile"},
 "mannequin":{"torso":"olive_textile","arm_0":"olive_textile","arm_1":"olive_textile","leg_0":"sand_textile","leg_1":"sand_textile","head":"graphite"},
 "shelter":{"roof":"cool_steel","back":"cool_steel","post_0":"safety_amber","post_1":"safety_amber"},
 "supply_station":{"cabinet":"signal_blue","console":"graphite","knob":"safety_amber"},
 "planter":{"soil":"earth","plant_0":"foliage","plant_1":"foliage","plant_2":"foliage"},
 "terrain_tile":{"ground":"earth","ridge_a":"earth","ridge_b":"earth"},
 "yard_composition":{"cabinet":"signal_blue","post_a":"safety_amber","post_b":"safety_amber"},
}
for name,choices in PALETTE.items():
    for p in PILOTS[name][1]:
        if p["id"] in choices:p["material"]=choices[p["id"]]


def authored_contract(parts):
    lo=[min(p["center"][i]-p["size"][i]/2 for p in parts) for i in range(3)]
    hi=[max(p["center"][i]+p["size"][i]/2 for p in parts) for i in range(3)]
    pivots={"anchor":[0,0,0]}
    for p in parts:
        x,y,z=p["center"];pivots[p["id"]]=[x,y-p["size"][1]/2,z]
    return {"unit":"m","up":"+Y","dimensions_m":[b-a for a,b in zip(lo,hi)],
            "pivots_local_m":pivots,"forward":{"node":"anchor","local_axis":[0,0,-1],"world_axis":[0,0,-1]},
            "tolerance_m":.001},lo,hi

def mesh_for(p,level,name=None):
    if name in RIG_NAMES:return shape(name,p,level)
    if name in ART_NAMES:
        art=detailed(name,p,level)
        if art is not None:return art
    x,y,z=p["size"];rx,rz=x/2,z/2
    if p["kind"]=="box":
        from .organic import CustomTopology
        v=((-rx,0,-rz),(rx,0,-rz),(rx,0,rz),(-rx,0,rz),(-rx,y,-rz),(rx,y,-rz),(rx,y,rz),(-rx,y,rz))
        f=((0,1,2,3),(4,7,6,5),(0,4,5,1),(1,5,6,2),(2,6,7,3),(3,7,4,0))
        return PythonBackend().build(CustomTopology(p["id"],v,f,True))
    if p["kind"]=="chamfer":return bevel_block(p["id"],p["size"],level)
    # Exact extrema at central ring, softened ends, authored ground pivot.
    profile=((0,.72),(.2,.94),(.5,1),(.8,.92),(1,.68))
    if p["id"].startswith("finger"):profile=((0,.88),(.18,.99),(.5,1),(.83,.90),(1,.52))
    elif p["id"] in ("torso","palm"):profile=((0,.78),(.2,.88),(.5,1),(.8,.96),(1,.72))
    elif p["id"].startswith("plant"):profile=((0,.36),(.2,.72),(.5,1),(.8,.63),(1,.20))
    elif p["id"].startswith("wheel"):profile=((0,.86),(.2,1),(.5,1),(.8,1),(1,.86))
    sections=tuple(LoftSection(y*t,(0,0),(rx*k,rz*k)) for t,k in profile)
    # effect budget is small: same mesh geometry, smaller authored resolution.
    seg=(24,12,8)[level] if p["id"]=="signal_volume" else SEGMENTS[level]
    return PythonBackend().build(OrganicLoft(p["id"],sections,seg,(2,1,1)[level]))

def generate(name,root,out,revision,lib,sources):
    category,parts,reference=PILOTS[name]
    contract,lo,hi=authored_contract(parts)
    folder=out/name;folder.mkdir(parents=True)
    rows=[];rig_meta=None
    for level in range(3):
        meshes=tuple(mesh_for(p,level,name) for p in parts)
        nodes=(NodeSpec("anchor"),)+tuple(NodeSpec(p["id"],p["id"],"anchor",p["material"],Transform.translation(contract["pivots_local_m"][p["id"]])) for p in parts)
        scene=SceneSpec("pilot_"+name,meshes,tuple(lib.material(k) for k in sorted({p["material"] for p in parts})),nodes)
        rig=None;level_contract=contract
        if name in RIG_NAMES:
            scene,rig,rig_meta=make_rig(name,parts,meshes,lib,contract["pivots_local_m"])
            meshes=scene.meshes
            level_contract={**contract,"pivots_local_m":{"anchor":[0,0,0],**{p["id"]:[0,0,0] for p in parts},**{"bone:"+b.id:list(b.rest_local.matrix[12:15]) for b in rig.skeleton.bones}}}
        target=folder/f"lod{level}"
        write_bundle(target,export_bundle(scene,tuple(build_render_mesh(m) for m in meshes),lib,sources=sources,rig=rig))
        for filename in ("asset.glb","asset.gltf"):
            row=Audit(target,filename,category,True,root,level_contract).run()
            if row["errors"]:raise ValueError((name,level,row["errors"]))
            if row["metrics"]["triangles"]>BUDGETS[category].triangles[level]:raise ValueError((name,level,"triangle budget exceeded"))
            row["level"]=level;row["rig"]=rig_meta;rows.append(row)
    tris=[r["metrics"]["triangles"] for r in rows if r["path"]=="asset.glb"]
    if category!="collision" and not tris[0]>tris[1]>tris[2]:raise ValueError((name,"LOD reduction missing",tris))
    if category=="collision" and len(set(tris))!=1:raise ValueError("collision proxy must stay invariant")
    result={"id":"qa:"+name,"slug":name,"category":category,"revision":revision,"contract":level_contract,"rig":rig_meta,
        "bounds_min_m":lo,"bounds_max_m":hi,"reference":reference,"source":"tools/asset_pipeline/parametric/pilot_suite.py",
        "art_backend":"Blender angle-limited bevel at LOD0" if name in ART_NAMES else "Python parametric","exports":rows,"collision":{"type":"box","size_m":[.60,1.0,.60],"center_m":[0,.50,0],"independent":True} if category=="collision" else None,"lod_distances_m":None,
        "budget_scope":"assembled individual QA asset; provisional; no distance integration","visual_approval":False,"production_integrated":False}
    (folder/"pilot-report.json").write_bytes(canonical(result))
    print("SUITE_EXPORT_PASS",name,tris,flush=True)
    return name

def main():
    p=argparse.ArgumentParser();p.add_argument("output");p.add_argument("revision");a=p.parse_args()
    out=Path(a.output);out.mkdir(parents=True,exist_ok=True)
    root=Path(__file__).resolve().parents[3]
    sources=source_manifest(root,[str(p.relative_to(root)) for p in Path(__file__).parent.glob("*.py")],a.revision)
    backend=BlenderBackend()
    if not backend.available:raise RuntimeError('Blender required for canonical artistic pilots; no fallback')
    print('ART_BLENDER_VERSION',subprocess.check_output([backend.executable,'--version'],text=True).splitlines()[0],flush=True)
    lib=finished_library(256,9133)
    names=[generate(name,root,out,a.revision,lib,sources) for name in sorted(PILOTS)]
    (out/"suite.json").write_bytes(canonical({"revision":a.revision,"pilots":names,"approved":False}))
if __name__=="__main__":main()
