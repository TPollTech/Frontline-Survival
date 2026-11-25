"""Bounded multi-joint deformation regression for the existing QA rigs.

Rotations use the existing bind-local X axis convention. Samples are
stress tests, not a complete animation, IK or anatomical ROM model.
"""
import math
from .rig import rotation
from .model import sub,cross,dot
from .intersection_audit import audit

POSES={
    "glove":{
        "wrist_and_two_fingers":{"wrist":12,"finger_1_j0":15,"finger_1_j1":25,"finger_2_j0":20,"finger_2_j1":20},
        "thumb_and_index":{"thumb_j0":15,"thumb_j1":15,"finger_0_j0":15,"finger_0_j1":20},
        "wrist_extension_and_little":{"wrist":-10,"finger_3_j0":15,"finger_3_j1":20},
    },
    "mannequin":{
        "bilateral_arm_flexion":{"arm_0_upper":15,"arm_0_lower":25,"arm_1_upper":-15,"arm_1_lower":20},
        "asymmetric_legs_and_head":{"leg_0_upper":10,"leg_0_lower":20,"leg_1_upper":-10,"head":10},
        "spine_arm_and_head":{"spine":8,"arm_0_upper":15,"head":-10},
    },
}
FRACTIONS=(.25,.5,.75,1.)

def triangle_area(v,face):
    a,b,c=(v[i] for i in face)
    n=cross(sub(b,a),sub(c,a))
    return .5*math.sqrt(dot(n,n))

def evaluate(name,mesh,skin,skeleton):
    rest=mesh.vertices
    faces=mesh.triangles
    areas=[triangle_area(rest,f) for f in faces]
    if any(a<=0 for a in areas):raise ValueError("degenerate rest face")
    result=[]
    for label,angles in POSES[name].items():
        samples=[]
        for fraction in FRACTIONS:
            pose={bone:rotation((1,0,0),math.radians(deg*fraction)) for bone,deg in angles.items()}
            deformed=skin.deform(mesh,skeleton,pose)
            ratios=[triangle_area(deformed,f)/area for f,area in zip(faces,areas)]
            moved=sum(math.dist(a,b)>1e-5 for a,b in zip(rest,deformed))
            contacts=audit(deformed,faces)
            sample={"fraction":fraction,"moved_vertices":moved,"min_area_ratio":min(ratios),"max_area_ratio":max(ratios),"contacts":contacts}
            if not moved or not all(math.isfinite(x) and .025<=x<=8 for x in ratios) or contacts["contact_pairs"]:
                raise ValueError(("combined pose gate",name,label,sample))
            samples.append(sample)
        result.append({"id":label,"axis":[1,0,0],"degrees":angles,"samples":samples})
    return result
