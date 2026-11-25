"""Authorial QA-only visual pilots. No gameplay behavior or production replacements."""
import argparse
from pathlib import Path
from .model import SceneSpec,NodeSpec,Transform
from .recipes import PythonBackend,Extrusion
from .organic import OrganicLoft,LoftSection
from .shading import build_render_mesh
from .pbr import generate_library
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
 P("cuff","loft",(0,.025,0),(.085,.05,.055),"fabric"),
 P("palm","loft",(0,.078,0),(.092,.085,.040),"fabric"),
 *[P("finger_"+str(i),"loft",(x,.12+h/2,0),(.018,h,.021),"rubber") for i,(x,h) in enumerate([(-.032,.058),(-.011,.076),(.011,.071),(.032,.052)])],
 P("thumb","loft",(-.052,.095,.008),(.024,.055,.028),"rubber")],
 "gloved hand study with five separate poseable nodes; not anatomical skinning"),
 "mannequin":("character",[
 P("torso","loft",(0,1.20,0),(.48,.52,.25),"fabric"),
 P("head","loft",(0,1.66,0),(.22,.28,.22),"rubber"),
 *[P("leg_"+str(i),"loft",(x,.45,0),(.16,.83,.16),"fabric") for i,x in enumerate([-.11,.11])],
 *[P("arm_"+str(i),"loft",(x,1.15,0),(.13,.52,.14),"fabric") for i,x in enumerate([-.30,.30])],
 *[P("boot_"+str(i),"chamfer",(x,.065,-.045),(.17,.13,.30),"rubber") for i,x in enumerate([-.11,.11])]],
 "static clothed mannequin with independent limb pivots; no skeleton or animation homologation"),
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
 P("ridge_a","loft",(-.9,.28,.5),(1.8,.36,1.3),"concrete"),
 P("ridge_b","loft",(1.0,.22,-.8),(1.4,.24,1.5),"concrete")],
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
SEGMENTS=(32,16,8)

def authored_contract(parts):
    lo=[min(p["center"][i]-p["size"][i]/2 for p in parts) for i in range(3)]
    hi=[max(p["center"][i]+p["size"][i]/2 for p in parts) for i in range(3)]
    pivots={"anchor":[0,0,0]}
    for p in parts:
        x,y,z=p["center"];pivots[p["id"]]=[x,y-p["size"][1]/2,z]
    return {"unit":"m","up":"+Y","dimensions_m":[b-a for a,b in zip(lo,hi)],
            "pivots_local_m":pivots,"forward":{"node":"anchor","local_axis":[0,0,-1],"world_axis":[0,0,-1]},
            "tolerance_m":.001},lo,hi

def mesh_for(p,level):
    x,y,z=p["size"];rx,rz=x/2,z/2
    if p["kind"]=="chamfer":
        d=min(rx,rz)*.18
        profile=((-rx+d,-rz),(rx-d,-rz),(rx,-rz+d),(rx,rz-d),(rx-d,rz),(-rx+d,rz),(-rx,rz-d),(-rx,-rz+d))
        return PythonBackend().build(Extrusion(p["id"],profile,y))
    # Exact extrema at central ring, softened ends, authored ground pivot.
    sections=tuple(LoftSection(y*t,(0,0),(rx*s,rz*s)) for t,s in ((0,.72),(.2,.94),(.5,1),(.8,.92),(1,.68)))
    return PythonBackend().build(OrganicLoft(p["id"],sections,SEGMENTS[level],(2,1,1)[level]))

def generate(name,root,out,revision,lib,sources):
    category,parts,reference=PILOTS[name]
    contract,lo,hi=authored_contract(parts)
    folder=out/name;folder.mkdir(parents=True)
    rows=[]
    for level in range(3):
        meshes=tuple(mesh_for(p,level) for p in parts)
        nodes=(NodeSpec("anchor"),)+tuple(NodeSpec(p["id"],p["id"],"anchor",p["material"],Transform.translation(contract["pivots_local_m"][p["id"]])) for p in parts)
        scene=SceneSpec("pilot_"+name,meshes,tuple(lib.material(k) for k in sorted({p["material"] for p in parts})),nodes)
        target=folder/f"lod{level}"
        write_bundle(target,export_bundle(scene,tuple(build_render_mesh(m) for m in meshes),lib,sources=sources))
        for filename in ("asset.glb","asset.gltf"):
            row=Audit(target,filename,category,True,root,contract).run()
            if row["errors"]:raise ValueError((name,level,row["errors"]))
            if row["metrics"]["triangles"]>BUDGETS[category].triangles[level]:raise ValueError((name,level,"triangle budget exceeded"))
            row["level"]=level;rows.append(row)
    tris=[r["metrics"]["triangles"] for r in rows if r["path"]=="asset.glb"]
    if not tris[0]>tris[1]>tris[2]:raise ValueError((name,"LOD reduction missing",tris))
    result={"id":"qa:"+name,"slug":name,"category":category,"revision":revision,"contract":contract,
        "bounds_min_m":lo,"bounds_max_m":hi,"reference":reference,"source":"tools/asset_pipeline/parametric/pilot_suite.py",
        "exports":rows,"collision":None,"lod_distances_m":None,
        "budget_scope":"assembled individual QA asset; provisional; no distance integration","visual_approval":False,"production_integrated":False}
    (folder/"pilot-report.json").write_bytes(canonical(result))
    print("SUITE_EXPORT_PASS",name,tris,flush=True)
    return name

def main():
    p=argparse.ArgumentParser();p.add_argument("output");p.add_argument("revision");a=p.parse_args()
    out=Path(a.output);out.mkdir(parents=True,exist_ok=True)
    root=Path(__file__).resolve().parents[3]
    sources=source_manifest(root,[str(p.relative_to(root)) for p in Path(__file__).parent.glob("*.py")],a.revision)
    lib=generate_library(64,9133)
    names=[generate(name,root,out,a.revision,lib,sources) for name in sorted(PILOTS)]
    (out/"suite.json").write_bytes(canonical({"revision":a.revision,"pilots":names,"approved":False}))
if __name__=="__main__":main()
