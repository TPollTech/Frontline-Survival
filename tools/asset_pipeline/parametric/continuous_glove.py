"""Single closed, branching hand surface with authored quad flow, QA only.

The surface is constructed from shared wrist/palm, four finger strips and an
oblique thumb strip. No overlapping or disconnected primitive shells. Two
skin layers and a closed perimeter form one manifold. Not a scan or a
production hand: approximate fictional adult work glove, one material.
"""
import math
from dataclasses import replace
from collections import Counter
from .model import MeshSpec,SceneSpec,NodeSpec,Transform
from .rig import BoneSpec,SkeletonSpec,SkinSpec,RigSpec,rotation
from .pbr import TextureData,MaterialLibrary
from .shading import build_render_mesh
from .intersection_audit import audit

LOW=(-.078,0.,-.022)
HIGH=(.048,.192,.022)
BANDS=(-.045,-.025,-.022,-.002,.002,.022,.025,.045)
LENGTHS=(.064,.080,.074,.055)
FINGER_T=(0,.16,.32,.44,.60,.76,.9,1)
THUMB_T=(0,.18,.36,.52,.76,1)
MATERIAL="glove_continuous"

def smooth(x):
    x=max(0.,min(1.,x))
    return x*x*(3-2*x)

def blend(a,b,t):
    if a==b or t<1e-8:return ((a,1.),)
    if t>1-1e-8:return ((b,1.),)
    return ((a,1-t),(b,t))

def digit_weights(id,t,joints):
    if t<.18:return blend("palm",id+"_j0",smooth(t/.18))
    for i,u in enumerate(joints[1:],1):
        if t<u-.09:return ((id+"_j"+str(i-1),1.),)
        if t<=u+.09:return blend(id+"_j"+str(i-1),id+"_j"+str(i),smooth((t-u+.09)/.18))
    return ((id+"_j"+str(len(joints)-1),1.),)

def glove_library(lib,size=512):
    """Authored atlas with subtle fabric weave, grip panels and stitch rows."""
    original=lib.material("olive_textile")
    base=[];orm=[];normal=[]
    for j in range(size):
        v=1-(j+.5)/size
        for i in range(size):
            u=(i+.5)/size
            face=(u-.04)/.44 if u<.5 else (u-.52)/.44
            x=LOW[0]+face*(HIGH[0]-LOW[0]);y=(v-.04)/.82*HIGH[1]
            grip=u>=.5 and ((abs(x)/.039)**4+(abs(y-.076)/.032)**4<1)
            grip_rib=grip and int(y*640)%5==0
            knuckle=u<.5 and y>.094 and y<.125 and -.043<x<.043
            cuff=y<.028 and v<.86
            seam=abs(y-.031)<.0012 or abs(y-.102)<.0008
            thread=seam and (int(u*185)%3!=0)
            weave=math.sin(i*math.pi/2)*math.sin(j*math.pi/2)
            grain=((i*37+j*17+i*j*13)%19-9)/9
            color=(57,61,48) if grip or knuckle else (80,86,62) if not cuff else (59,64,47)
            if grip_rib:color=(65,69,54)
            if thread:color=(105,111,86)
            base.extend(max(0,min(255,round(c+2.5*weave+2*grain))) for c in color)
            orm.extend((238 if seam else 250,195 if grip else 218 if knuckle else 232,0))
            nx=.085*math.cos(i*math.pi/2);ny=.085*math.cos(j*math.pi/2)+(.12*math.sin(y*640*2*math.pi/5) if grip else 0.)
            normal.extend(round((q*.5+.5)*255) for q in (nx,ny,math.sqrt(1-nx*nx-ny*ny)))
    tex=[TextureData(MATERIAL+"_"+role,role,size,size,bytes(data),"procedural:continuous_glove_atlas_v2","original project asset") for role,data in (("base_color",base),("orm",orm),("normal",normal))]
    mat=replace(original,id=MATERIAL,base_color_texture=tex[0].id,orm_texture=tex[1].id,normal_texture=tex[2].id,normal_scale=.45)
    return MaterialLibrary([*lib.materials,mat],[*lib.textures,*tex])

def build_glove(level,lib):
    n=(6,4,2)[level];ny=(3,2,1)[level]
    points=[];weights=[];quads=[]
    def add(x,y,thickness,w):
        i=len(points);points.append((x,y,thickness));weights.append(w);return i
    def connect(a,b):
        assert len(a)==len(b)
        quads.extend((a[i],a[i+1],b[i+1],b[i]) for i in range(len(a)-1))
    # Palm columns: four finger-root bands separated by narrow web strips.
    xs=[BANDS[0]];bands=[]
    for i,(a,b) in enumerate(zip(BANDS,BANDS[1:])):
        count=n if i%2==0 else max(1,n//3)
        start=len(xs)-1
        xs.extend(a+(b-a)*j/count for j in range(1,count+1))
        if i%2==0:bands.append((start,len(xs)-1))
    stations=((0,.68,.018),(.024,.77,.020),(.052,.96,.021),(.082,16/15,.022),(.105,1.,.019),(.112,1.,.014))
    rows=[];station_rows=[]
    for k,(y,s,z) in enumerate(stations):
        if k==0:steps=[(y,s,z)]
        else:
            ay,as_,az=stations[k-1]
            steps=[(ay+(y-ay)*j/ny,as_+(s-as_)*j/ny,az+(z-az)*j/ny) for j in range(1,ny+1)]
        for yy,ss,zz in steps:
            row=[add(x*ss,yy,zz*(.62+.38*math.sqrt(max(0,1-(x/.045)**2))),blend("wrist","palm",smooth((yy-.018)/.034))) for x in xs]
            if rows:connect(rows[-1],row)
            rows.append(row)
        station_rows.append(len(rows)-1)
    root=rows[-1];joints={}
    for f,(start,end) in enumerate(bands):
        id="finger_"+str(f);length=LENGTHS[f]
        previous=root[start:end+1];center=(xs[start]+xs[end])/2
        joints[id]=[(center,.112+length*t,0.) for t in (0,.44,.76)]
        for t,width in zip(FINGER_T[1:],(.99,.98,.93,.86,.80,.72,.48)):
            row=[]
            for k in range(n+1):
                u=k/n;cross=2*u-1
                x=center+(xs[end]-xs[start])*cross*width/2
                y=.112+length*t-(.0018*cross*cross if t==1 else 0)
                thick=.0105*width*(.65+.35*math.sqrt(max(0,1-cross*cross)))
                row.append(add(x,y,thick,digit_weights(id,t,(0,.44,.76))))
            connect(previous,row);previous=row
    # Thumb shares a genuine edge of the palm; it diverges diagonally.
    previous=[rows[i][0] for i in range(station_rows[2],station_rows[3]+1)]
    root_positions=[points[i] for i in previous]
    cx=sum(v[0] for v in root_positions)/len(root_positions)
    cy=sum(v[1] for v in root_positions)/len(root_positions)
    def thumb_center(t):return (cx+(-.075-cx)*t,cy+(.112-cy)*t,0.)
    joints["thumb"]=[thumb_center(t) for t in (0,.52)]
    for t,width in zip(THUMB_T[1:],(.98,.91,.82,.65,.40)):
        row=[];center=thumb_center(t)
        for k,(x,y,z) in enumerate(root_positions):
            u=k/(len(root_positions)-1);cross=2*u-1
            dx=((x-cx)*(1-t)+.008*cross*t)*width
            dy=((y-cy)*(1-t)+.008*cross*t)*width
            row.append(add(center[0]+dx,center[1]+dy,.013*width*(.65+.35*math.sqrt(max(0,1-cross*cross))),digit_weights("thumb",t,(0,.52))))
        connect(previous,row);previous=row
    # Boundary determined from the actual quad incidence. Shared edges are
    # never duplicated or capped internally.
    incidence=Counter(tuple(sorted((a,b))) for q in quads for a,b in zip(q,q[1:]+q[:1]))
    edges=[(a,b) for q in quads for a,b in zip(q,q[1:]+q[:1]) if incidence[tuple(sorted((a,b)))]==1]
    if any(v>2 for v in incidence.values()):raise ValueError("nonmanifold patch")
    boundary={a for a,b in edges};next_edge=dict(edges)
    if len(boundary)!=len(edges):raise ValueError("branching perimeter")
    loop=[min(boundary)]
    while next_edge[loop[-1]]!=loop[0]:
        nxt=next_edge[loop[-1]]
        if nxt in loop:raise ValueError("perimeter cycle")
        loop.append(nxt)
    if len(loop)!=len(edges):raise ValueError("more than one perimeter")
    # Rounded edge cross-section; independent envelope is an authored target.
    half=[(x,y,z*(.47 if i in boundary else 1.)) for i,(x,y,z) in enumerate(points)]
    size=len(half);raw=half+[(x,y,-z) for x,y,z in half]
    lo=tuple(min(v[i] for v in raw) for i in range(3));hi=tuple(max(v[i] for v in raw) for i in range(3))
    def fit(v):return tuple(LOW[i]+(v[i]-lo[i])/(hi[i]-lo[i])*(HIGH[i]-LOW[i]) for i in range(3))
    vertices=tuple(fit(v) for v in raw)
    tris=[];uv=[]
    def face(a,b,c,chart):
        tris.append((a,b,c));uv.extend(chart(i) for i in (a,b,c))
    def chart(i,back=False):
        x,y,z=vertices[i];u=(x-LOW[0])/(HIGH[0]-LOW[0]);v=(y-LOW[1])/(HIGH[1]-LOW[1])
        return ((.52 if back else .04)+.44*u,.04+.82*v)
    for a,b,c,d in quads:
        face(a,b,c,chart);face(a,c,d,chart)
        back=lambda i:chart(i,True)
        face(a+size,c+size,b+size,back);face(a+size,d+size,c+size,back)
    distances=[0.]
    for a,b in zip(loop,loop[1:]+loop[:1]):distances.append(distances[-1]+math.dist(vertices[a],vertices[b]))
    for k,(a,b) in enumerate(zip(loop,loop[1:]+loop[:1])):
        u0=.02+.96*distances[k]/distances[-1];u1=.02+.96*distances[k+1]/distances[-1]
        mapping={a:(u0,.98),b:(u1,.98),a+size:(u0,.90),b+size:(u1,.90)}
        face(b,a,a+size,mapping.__getitem__);face(b,a+size,b+size,mapping.__getitem__)
    mesh=MeshSpec("glove_surface",vertices,tuple(tris))
    if not mesh.closed_oriented() or mesh.signed_volume()<=0:raise ValueError("invalid continuous glove")
    # One connected component, Euler characteristic of a genus-zero shell.
    graph=[set() for _ in vertices];edge_set=set()
    for a,b,c in tris:
        for u,v in ((a,b),(b,c),(c,a)):
            graph[u].add(v);graph[v].add(u);edge_set.add(tuple(sorted((u,v))))
    seen={0};stack=[0]
    while stack:
        for j in graph[stack.pop()]-seen:seen.add(j);stack.append(j)
    if len(seen)!=len(vertices) or len(vertices)-len(edge_set)+len(tris)!=2:raise ValueError("not a single genus-zero surface")
    # Stable anatomical rest pivots in the same fitted bind frame.
    bones=[];pos={}
    def bone(id,parent,p,length):
        p=fit(p);q=pos[parent] if parent else (0,0,0);pos[id]=p
        bones.append(BoneSpec(id,parent,Transform.translation(tuple(a-b for a,b in zip(p,q))),length))
    bone("wrist",None,(0,0,0),.035);bone("palm","wrist",(0,.035,0),.077)
    for id,chain in joints.items():
        parent="palm"
        for i,p in enumerate(chain):
            k=id+"_j"+str(i);length=math.dist(p,chain[i+1]) if i+1<len(chain) else .015
            bone(k,parent,p,length);parent=k
    sk=SkeletonSpec("glove_skeleton",tuple(bones))
    skin=SkinSpec(mesh.id,sk.id,tuple(weights+weights))
    scene=SceneSpec("pilot_glove",(mesh,),(lib.material(MATERIAL),),(NodeSpec("anchor"),NodeSpec(mesh.id,mesh.id,"anchor",MATERIAL)))
    rig=RigSpec("pilot_rig",scene,sk,"anchor",(skin,))
    render=build_render_mesh(mesh,uv=tuple(uv),crease_rad=math.pi*.85)
    # Check multiple local rotations using source-vertex LBS, not only child displacement.
    checks=[]
    for id,deg in (("wrist",20),("finger_1_j1",45),("finger_2_j0",35),("thumb_j0",25)):
        deformed=skin.deform(mesh,sk,{id:rotation((1,0,0),math.radians(deg))})
        def area(a,b,c):
            p,q,r=(a,b,c);u=tuple(q[i]-p[i] for i in range(3));v=tuple(r[i]-p[i] for i in range(3))
            return math.sqrt(sum((u[(i+1)%3]*v[(i+2)%3]-u[(i+2)%3]*v[(i+1)%3])**2 for i in range(3)))
        ratios=[area(*(deformed[i] for i in f))/area(*(vertices[i] for i in f)) for f in tris]
        moved=sum(math.dist(a,b)>1e-5 for a,b in zip(vertices,deformed))
        if not moved or min(ratios)<.025 or max(ratios)>8:raise ValueError(("unstable deformation",id,min(ratios),max(ratios)))
        checks.append({"bone":id,"degrees":deg,"moved_vertices":moved,"min_area_ratio":min(ratios),"max_area_ratio":max(ratios),"contacts":audit(deformed,tris)})
    contract={"unit":"m","up":"+Y","dimensions_m":[b-a for a,b in zip(LOW,HIGH)],"pivots_local_m":{"anchor":[0,0,0],mesh.id:[0,0,0],**{"bone:"+b.id:list(b.rest_local.matrix[12:15]) for b in sk.bones}},"forward":{"node":"anchor","local_axis":[0,0,-1],"world_axis":[0,0,-1]},"tolerance_m":.001}
    rest_contacts=audit(vertices,tris)
    if rest_contacts["contact_pairs"] or any(c["contacts"]["contact_pairs"] for c in checks):
        raise ValueError(("glove nonadjacent contact gate",level,rest_contacts,checks))
    meta={"bone_count":len(bones),"parents":{b.id:b.parent_id for b in sk.bones},"pose_bone":"finger_1_j1","pose_child":"finger_1_j2","pose_degrees":25,"skin_meshes":1,"mixed_vertices":sum(len(w)>1 for w in skin.weights),"components":1,"euler_characteristic":2,"source_vertices":len(vertices),"quad_patches":len(quads),"rest_contacts":rest_contacts,"deformation_checks":checks}
    return scene,render,rig,meta,contract
