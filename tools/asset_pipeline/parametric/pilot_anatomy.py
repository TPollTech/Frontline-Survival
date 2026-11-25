"""QA-only articulated glove and clothed mannequin, explicit rest joints and LBS.

Dimensions are original approximate adult proportions, not a medical model.
Skin weights are deterministic by authored longitudinal joint locations.
Separate material shells remain separate; no continuous anatomical retopology.
"""
from .model import MeshSpec,SceneSpec,NodeSpec,Transform
from .rig import BoneSpec,SkeletonSpec,SkinSpec,RigSpec
from .organic import OrganicLoft,LoftSection
from .recipes import PythonBackend
from .pilot_finish import bevel_block

RIG_NAMES=frozenset(("glove","mannequin"))
def shape(name,p,level):
    x,y,z=p["size"];id=p["id"]
    if id.startswith("boot"):return bevel_block(id,p["size"],level)
    # Radii at the mid ring establish the authored dimensional envelope.
    profiles={
        "palm":((0,.69,.83),(.20,.80,.94),(.50,1,1),(.78,.94,.81),(1,.86,.65)),
        "cuff":((0,.93,.95),(.2,1,1),(.5,1,1),(.8,.90,.92),(1,.86,.88)),
        "torso":((0,.77,.86),(.23,.76,.78),(.50,.93,.96),(.66,1,1),(.85,.91,.87),(1,.48,.64)),
        "head":((0,.49,.62),(.20,.74,.82),(.50,1,1),(.78,.95,.95),(1,.32,.39)),
        "thumb":((0,.90,.91),(.18,.98,.97),(.50,1,1),(.78,.81,.82),(1,.47,.48)),
    }
    if id.startswith("finger"):profile=((0,.88,.91),(.18,.96,.93),(.34,1,1),(.54,.90,.89),(.72,.84,.88),(.88,.72,.75),(1,.37,.40))
    elif id.startswith("arm"):profile=((0,.53,.56),(.18,.70,.78),(.40,.72,.72),(.58,.82,.84),(.78,1,1),(1,.77,.78))
    elif id.startswith("leg"):profile=((0,.62,.68),(.19,.81,.89),(.42,.64,.73),(.59,.77,.80),(.82,1,1),(1,.90,.88))
    else:profile=profiles[id]
    # Keep enough axial sections at every level to support joint bending.
    sections=tuple(LoftSection(y*t,(0,0),(x*a/2,z*b/2)) for t,a,b in profile)
    return PythonBackend().build(OrganicLoft(id,sections,(32,16,8)[level],(2,1,1)[level]))

def make_rig(name,parts,meshes,lib,pivots):
    bones=[];positions={};bindings={}
    by={p["id"]:p for p in parts}
    def joint(id,parent,pos,length):
        prev=positions[parent] if parent else (0,0,0)
        bones.append(BoneSpec(id,parent,Transform.translation(tuple(a-b for a,b in zip(pos,prev))),length))
        positions[id]=pos
        return id
    def at(id,t):
        p=by[id];x,y,z=pivots[id]
        return (x,y+p["size"][1]*t,z)
    def bind(id,keys):
        bindings[id]=keys
    if name=="glove":
        joint("wrist",None,at("cuff",0),.05)
        joint("palm","wrist",at("palm",0),.075)
        bind("cuff",[(0,"wrist"),(1,"palm")]);bind("palm",[(0,"palm")])
        for id in [p["id"] for p in parts if p["id"].startswith("finger") or p["id"]=="thumb"]:
            length=by[id]["size"][1];fractions=(0,.44,.76) if id!="thumb" else (0,.52)
            parent="palm";keys=[]
            for i,t in enumerate(fractions):
                k=id+"_j"+str(i);joint(k,parent,at(id,t),length*((fractions[i+1] if i+1<len(fractions) else 1)-t));keys.append((t,k));parent=k
            bind(id,keys)
        pose="finger_1_j1";tip="finger_1_j2"
    else:
        joint("pelvis",None,(0,.88,0),.20)
        joint("spine","pelvis",(0,1.15,0),.30)
        joint("head","spine",at("head",0),.26)
        bind("torso",[(0,"pelvis"),(.55,"spine")]);bind("head",[(0,"head")])
        for i in range(2):
            arm="arm_"+str(i);leg="leg_"+str(i);boot="boot_"+str(i)
            upper=joint(arm+"_upper","spine",at(arm,.94),.27)
            lower=joint(arm+"_lower",upper,at(arm,.48),.26)
            bind(arm,[(0,lower),(.40,lower),(.65,upper),(1,upper)])
            upper=joint(leg+"_upper","pelvis",at(leg,.96),.42)
            lower=joint(leg+"_lower",upper,at(leg,.48),.40)
            foot=joint(boot+"_foot",lower,at(boot,.85),.15)
            bind(leg,[(0,lower),(.40,lower),(.65,upper),(1,upper)]);bind(boot,[(0,foot)])
        pose="arm_0_upper";tip="arm_0_lower"
    skeleton=SkeletonSpec(name+"_skeleton",tuple(bones))
    def weights(keys,t):
        if len(keys)==1 or t<=keys[0][0]:return ((keys[0][1],1.),)
        for (a,k),(b,l) in zip(keys,keys[1:]):
            if t<=b:
                if k==l:return ((k,1.),)
                v=(t-a)/(b-a)
                if v<1e-8:return ((k,1.),)
                if v>1-1e-8:return ((l,1.),)
                return ((k,1-v),(l,v))
        return ((keys[-1][1],1.),)
    shifted=[];skins=[];nodes=[NodeSpec("anchor")]
    for p,m in zip(parts,meshes):
        x,y,z=pivots[p["id"]]
        v=tuple((a+x,b+y,c+z) for a,b,c in m.vertices)
        shifted.append(MeshSpec(m.id,v,m.triangles))
        skins.append(SkinSpec(m.id,skeleton.id,tuple(weights(bindings[m.id],max(0,min(1,b/p["size"][1]))) for a,b,c in m.vertices)))
        nodes.append(NodeSpec(p["id"],m.id,"anchor",p["material"]))
    scene=SceneSpec("pilot_"+name,tuple(shifted),tuple(lib.material(k) for k in sorted({p["material"] for p in parts})),tuple(nodes))
    rig=RigSpec("pilot_rig",scene,skeleton,"anchor",tuple(skins))
    meta={"bone_count":len(bones),"parents":{b.id:b.parent_id for b in skeleton.bones},"pose_bone":pose,"pose_child":tip,"pose_degrees":25,
          "skin_meshes":len(skins),"mixed_vertices":sum(len(row)>1 for s in skins for row in s.weights)}
    if not meta["mixed_vertices"]:raise ValueError("no blended skin vertices")
    return scene,rig,meta
