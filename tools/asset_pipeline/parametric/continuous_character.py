"""Connected clothed humanoid QA study with authored branching quad strips.

No scanned anatomy, separate equipment or production animation. Rest A-pose,
continuous torso/neck/head/arms/legs/boots, explicit regional skin weights.
"""
import math
from collections import Counter
from dataclasses import replace
from .model import MeshSpec,SceneSpec,NodeSpec,Transform
from .rig import BoneSpec,SkeletonSpec,SkinSpec,RigSpec,rotation
from .pbr import TextureData,MaterialLibrary
from .shading import build_render_mesh
from .continuous_glove import blend,smooth
from .intersection_audit import audit

LOW=(-.49,0.,-.175)
HIGH=(.49,1.80,.155)
MATERIAL="character_continuous"

def character_library(lib,size=512):
    original=lib.material("olive_textile")
    base=[];orm=[];normal=[]
    for j in range(size):
        v=1-(j+.5)/size;y=(v-.04)/.82*1.8
        for i in range(size):
            u=(i+.5)/size;x=LOW[0]+((u-.04)/.44 if u<.5 else (u-.52)/.44)*(HIGH[0]-LOW[0])
            color=(83,88,67)
            if y<.88:color=(108,100,78)
            if y<.14 or (.83<y<.99 and abs(x)>.29):color=(45,49,43)
            if 1.57<y:color=(60,66,57)
            if .875<y<.94 and abs(x)<.22:color=(49,53,44)
            if 1.12<y<1.34 and .045<abs(x)<.17:color=(67,75,56)
            if abs(y-1.34)<.005 and abs(x)<.18:color=(111,116,91)
            if abs(abs(x)-.11)<.004 and .23<y<.7:color=(87,80,64)
            weave=math.sin(i*math.pi/2)*math.sin(j*math.pi/2)
            grain=((i*31+j*19+i*j*11)%23-11)/11
            base.extend(max(0,min(255,round(c+2*weave+2*grain))) for c in color)
            orm.extend((247,231 if y>.14 else 213,0))
            a=.065*math.cos(i*math.pi/2);b=.065*math.cos(j*math.pi/2)
            normal.extend(round((q*.5+.5)*255) for q in (a,b,math.sqrt(1-a*a-b*b)))
    tex=[TextureData(MATERIAL+"_"+role,role,size,size,bytes(data),"procedural:continuous_character_atlas_v1","original project asset") for role,data in (("base_color",base),("orm",orm),("normal",normal))]
    mat=replace(original,id=MATERIAL,base_color_texture=tex[0].id,orm_texture=tex[1].id,normal_texture=tex[2].id,normal_scale=.4)
    return MaterialLibrary([*lib.materials,mat],[*lib.textures,*tex])

def build_character(level,lib):
    n=(6,4,2)[level];ny=(3,2,1)[level]
    pts=[];weights=[];quads=[]
    def add(x,y,z,depth,w):
        k=len(pts);pts.append((x,y,z,depth));weights.append(w);return k
    def connect(a,b,reverse=False):
        if reverse:a,b=b,a
        quads.extend((a[i],a[i+1],b[i+1],b[i]) for i in range(len(a)-1))
    # Lower torso row is split into two hip bands; central strip is crotch.
    xs=[-1.];bands=[]
    for a,b,count in ((-1,-.13,n),(-.13,.13,max(2,n//2)),(.13,1,n)):
        start=len(xs)-1;xs.extend(a+(b-a)*j/count for j in range(1,count+1));bands.append((start,len(xs)-1))
    stations=((.88,.18,.103),(1.00,.186,.109),(1.16,.174,.105),(1.30,.207,.128),(1.39,.235,.132),(1.48,.224,.111),(1.54,.151,.092),(1.58,.082,.065))
    rows=[];st=[]
    for k,(y,w,d) in enumerate(stations):
        if k==0:steps=[(y,w,d)]
        else:
            a,b,c=stations[k-1]
            steps=[(a+(y-a)*j/ny,b+(w-b)*j/ny,c+(d-c)*j/ny) for j in range(1,ny+1)]
        for yy,ww,dd in steps:
            row=[add(x*ww,yy,0,dd*(.58+.42*math.sqrt(max(0,1-x*x))),blend("pelvis","spine",smooth((yy-.97)/.25))) for x in xs]
            if rows:connect(rows[-1],row)
            rows.append(row)
        st.append(len(rows)-1)
    # Neck/head uses the entire narrowed top row, not separate capped volume.
    previous=rows[-1]
    for y,w,d,z in ((1.615,.085,.075,0),(1.65,.106,.097,-.005),(1.71,.112,.102,-.008),(1.77,.095,.087,0),(1.80,.036,.04,0)):
        row=[add(x*w,y,z,d*(.55+.45*math.sqrt(max(0,1-x*x))),blend("spine","head",smooth((y-1.58)/.075))) for x in xs]
        connect(previous,row);previous=row
    # Leg strips share the pelvis lower edge; tapered boot toes face -Z.
    for side,band in enumerate((bands[0],bands[2])):
        sign=-1 if side==0 else 1;start,end=band
        previous=rows[0][start:end+1];upper="leg_"+str(side)+"_upper";lower="leg_"+str(side)+"_lower";foot="boot_"+str(side)+"_foot"
        for y,center,w,d,z in ((.80,.109,.087,.092,0),(.68,.117,.083,.085,0),(.56,.126,.067,.066,0),(.46,.134,.063,.063,.003),(.36,.141,.071,.071,.005),(.23,.145,.058,.060,.004),(.14,.148,.060,.078,-.016),(.075,.148,.081,.115,-.052),(.0,.148,.078,.10,-.053)):
            if y>.50:skin=blend(upper,"pelvis",smooth((y-.74)/.14))
            elif y>.37:skin=blend(lower,upper,smooth((y-.37)/.19))
            elif y>.12:skin=blend(foot,lower,smooth((y-.12)/.16))
            else:skin=((foot,1.),)
            row=[]
            for j in range(n+1):
                a=2*j/n-1
                row.append(add(sign*center+a*w,y,z,d*(.62+.38*math.sqrt(max(0,1-a*a))),skin))
            connect(previous,row,True);previous=row
    # Arm roots are side edges at chest/shoulder; A-pose branches.
    for side in range(2):
        sign=-1 if side==0 else 1;upper="arm_"+str(side)+"_upper";lower="arm_"+str(side)+"_lower";hand="hand_"+str(side)
        previous=[rows[i][0 if side==0 else -1] for i in range(st[3],st[5]+1)]
        root=[pts[i] for i in previous];cx=sum(p[0] for p in root)/len(root);cy=sum(p[1] for p in root)/len(root)
        count=len(previous)-1
        for t,dx,dy,w,d in ((.12,.075,-.02,.075,.077),(.25,.115,-.105,.070,.071),(.43,.157,-.218,.057,.062),(.55,.185,-.29,.053,.056),(.72,.221,-.39,.052,.058),(.85,.245,-.475,.038,.043),(.94,.263,-.525,.043,.035),(1,.272,-.575,.026,.024)):
            if t<.25:skin=blend("spine",upper,smooth(t/.25))
            elif t<.66:skin=blend(upper,lower,smooth((t-.38)/.24))
            elif t<.92:skin=blend(lower,hand,smooth((t-.72)/.20))
            else:skin=((hand,1.),)
            row=[]
            for j in range(count+1):
                a=2*j/count-1
                row.append(add(cx+sign*(dx+a*w*.90),cy+dy+a*w*.44,0,d*(.62+.38*math.sqrt(max(0,1-a*a))),skin))
            connect(previous,row,side==1);previous=row
    incidence=Counter(tuple(sorted((a,b))) for q in quads for a,b in zip(q,q[1:]+q[:1]))
    edges=[(a,b) for q in quads for a,b in zip(q,q[1:]+q[:1]) if incidence[tuple(sorted((a,b)))]==1]
    if any(v>2 for v in incidence.values()):raise ValueError("nonmanifold character patch")
    boundary={a for a,b in edges};next_edge=dict(edges)
    if len(boundary)!=len(edges):raise ValueError("branching perimeter")
    loop=[min(boundary)]
    while next_edge[loop[-1]]!=loop[0]:
        nxt=next_edge[loop[-1]]
        if nxt in loop:raise ValueError("perimeter cycle")
        loop.append(nxt)
    if len(loop)!=len(edges):raise ValueError("multiple perimeter loops")
    size=len(pts)
    raw=tuple((x,y,z+sign*d*(.42 if i in boundary else 1.)) for sign in (1,-1) for i,(x,y,z,d) in enumerate(pts))
    lo=tuple(min(v[i] for v in raw) for i in range(3));hi=tuple(max(v[i] for v in raw) for i in range(3))
    def fit(v):return tuple(LOW[i]+(v[i]-lo[i])/(hi[i]-lo[i])*(HIGH[i]-LOW[i]) for i in range(3))
    vs=tuple(fit(v) for v in raw);tris=[];uv=[]
    def face(a,b,c,chart):
        tris.append((a,b,c));uv.extend(chart(i) for i in (a,b,c))
    def chart(i,back=False):
        x,y,z=vs[i];u=(x-LOW[0])/(HIGH[0]-LOW[0]);v=y/HIGH[1]
        return ((.04 if back else .52)+.44*u,.04+.82*v)
    for a,b,c,d in quads:
        face(a,b,c,chart);face(a,c,d,chart)
        back=lambda i:chart(i,True)
        face(a+size,c+size,b+size,back);face(a+size,d+size,c+size,back)
    distances=[0.]
    for a,b in zip(loop,loop[1:]+loop[:1]):distances.append(distances[-1]+math.dist(vs[a],vs[b]))
    for k,(a,b) in enumerate(zip(loop,loop[1:]+loop[:1])):
        u0=.02+.96*distances[k]/distances[-1];u1=.02+.96*distances[k+1]/distances[-1]
        mapping={a:(u0,.98),b:(u1,.98),a+size:(u0,.90),b+size:(u1,.90)}
        face(b,a,a+size,mapping.__getitem__);face(b,a+size,b+size,mapping.__getitem__)
    mesh=MeshSpec("character_surface",vs,tuple(tris))
    if not mesh.closed_oriented() or mesh.signed_volume()<=0:raise ValueError("invalid character shell")
    graph=[set() for v in vs];edge_set=set()
    for a,b,c in tris:
        for u,v in ((a,b),(b,c),(c,a)):
            graph[u].add(v);graph[v].add(u);edge_set.add(tuple(sorted((u,v))))
    seen={0};stack=[0]
    while stack:
        for j in graph[stack.pop()]-seen:seen.add(j);stack.append(j)
    if len(seen)!=len(vs) or len(vs)-len(edge_set)+len(tris)!=2:raise ValueError("invalid connected topology")
    bones=[];pos={}
    def bone(id,parent,p,length):
        p=fit(p);q=pos[parent] if parent else (0,0,0);pos[id]=p
        bones.append(BoneSpec(id,parent,Transform.translation(tuple(a-b for a,b in zip(p,q))),length))
    bone("pelvis",None,(0,.88,0),.25);bone("spine","pelvis",(0,1.15,0),.4);bone("head","spine",(0,1.58,0),.22)
    for side in range(2):
        sign=-1 if side==0 else 1;upper="arm_"+str(side)+"_upper";lower="arm_"+str(side)+"_lower"
        bone(upper,"spine",(sign*.237,1.44,0),.29);bone(lower,upper,(sign*.39,1.18,0),.28);bone("hand_"+str(side),lower,(sign*.46,.98,0),.11)
        upper="leg_"+str(side)+"_upper";lower="leg_"+str(side)+"_lower"
        bone(upper,"pelvis",(sign*.102,.87,0),.39);bone(lower,upper,(sign*.134,.46,0),.38);bone("boot_"+str(side)+"_foot",lower,(sign*.148,.14,0),.14)
    sk=SkeletonSpec("character_skeleton",tuple(bones))
    skin=SkinSpec(mesh.id,sk.id,tuple(weights+weights))
    scene=SceneSpec("pilot_mannequin",(mesh,),(lib.material(MATERIAL),),(NodeSpec("anchor"),NodeSpec(mesh.id,mesh.id,"anchor",MATERIAL)))
    rig=RigSpec("pilot_rig",scene,sk,"anchor",(skin,))
    render=build_render_mesh(mesh,uv=tuple(uv),crease_rad=math.pi*.85)
    checks=[]
    for id,deg in (("arm_0_upper",25),("arm_1_lower",45),("leg_0_lower",35),("head",20)):
        deformed=skin.deform(mesh,sk,{id:rotation((1,0,0),math.radians(deg))})
        moved=sum(math.dist(a,b)>1e-5 for a,b in zip(vs,deformed))
        if not moved:raise ValueError("pose has no effect")
        checks.append({"bone":id,"degrees":deg,"moved_vertices":moved,"contacts":audit(deformed,tris)})
    contacts=audit(vs,tris)
    contract={"unit":"m","up":"+Y","dimensions_m":[b-a for a,b in zip(LOW,HIGH)],"pivots_local_m":{"anchor":[0,0,0],mesh.id:[0,0,0],**{"bone:"+b.id:list(b.rest_local.matrix[12:15]) for b in sk.bones}},"forward":{"node":"anchor","local_axis":[0,0,-1],"world_axis":[0,0,-1]},"tolerance_m":.001}
    meta={"bone_count":len(bones),"parents":{b.id:b.parent_id for b in sk.bones},"pose_bone":"arm_0_upper","pose_child":"arm_0_lower","pose_degrees":25,"skin_meshes":1,"mixed_vertices":sum(len(w)>1 for w in skin.weights),"components":1,"euler_characteristic":2,"source_vertices":len(vs),"quad_patches":len(quads),"rest_contacts":contacts,"deformation_checks":checks}
    return scene,render,rig,meta,contract
