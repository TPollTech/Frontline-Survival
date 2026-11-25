"""Art-direction pass for three QA-only industrial concepts.

References (observed, not copied): Rittal outdoor enclosure canopy, door joints,
louvers and base plinth; DirectIndustry CS Toptec product photo.
All dimensions are original fictional art-direction choices, not a CAD replica.
"""
from .model import MeshSpec
from .recipes import PythonBackend,Box,Revolution
from .blender_backend import BlenderBackend
from .pilot_finish import bevel_block

ART_NAMES=frozenset(("supply_station","shelter","utility_cart"))
BACKEND_PARTS=frozenset((("supply_station","cabinet"),("shelter","roof"),("utility_cart","cab")))
def combine(id,items):
    vertices=[];triangles=[]
    for mesh,offset in items:
        start=len(vertices)
        vertices.extend(tuple(v[i]+offset[i] for i in range(3)) for v in mesh.vertices)
        triangles.extend(tuple(start+i for i in face) for face in mesh.triangles)
    return MeshSpec(id,vertices,triangles)

def panel(id,size,level,blender=False):
    if blender and level==0:
        base=PythonBackend().build(Box(id,size))
        mesh=BlenderBackend().bevel(base,min(size)*.065,segments=3)
        # The Box recipe is centered; place its authored lower face at y=0.
        return combine(id,[(mesh,(0,size[1]/2,0))])
    return bevel_block(id,size,level)

def detailed(name,p,level):
    id=p["id"];x,y,z=p["size"]
    if (name,id) in BACKEND_PARTS:
        items=[]
        def add(label,size,offset,blender=False):
            items.append((panel(label,size,level,blender),offset))
        if name=="supply_station":
            # Outer shell has exact envelope; door and raised louvers sit in
            # the reserved front thickness, not coincident with the shell.
            add("enclosure",(x,y,z*.82),(0,0,z*.09),True)
            add("door",(x*.89,y*.90,z*.10),(0,y*.05,-z*.38))
            add("vent_surround",(x*.52,y*.27,z*.045),(0,y*.13,-z*.435))
            for i in range((7,4,2)[level]):
                add("louver_"+str(i),(x*.46,y*.018,z*.07),(0,y*(.145+i*.22/(7,4,2)[level]),-z*.465))
            # Door hinges and raised latch. Small details remain within the
            # cabinet's original physical envelope and material group.
            for i in range(2 if level<2 else 1):
                add("hinge_"+str(i),(x*.035,y*.095,z*.055),(-x*.455,y*(.18+i*.56),-z*.4725))
            add("latch",(x*.045,y*.12,z*.065),(x*.34,y*.52,-z*.4675))
        elif name=="shelter":
            add("canopy",(x,y*.64,z),(0,y*.36,0),True)
            add("underframe",(x*.92,y*.25,z*.89),(0,y*.11,0))
            for i in range((5,3,2)[level]):
                add("rib_"+str(i),(x*.025,y*.11,z*.82),(x*(-.39+i*.78/max(1,(5,3,2)[level]-1)),0,0))
        else:
            add("cab_body",(x,y*.80,z),(0,0,0),True)
            add("roof",(x,y*.20,z),(0,y*.80,0))
            # Side pressed-panel strips lie within the silhouette.
        return combine(id,items)
    if name=="shelter" and id=="back":
        items=[(panel("backing",(x,y,z*.65),level),(0,0,z*.175))]
        n=(12,6,3)[level]
        for i in range(n):
            off=-x*.45+i*x*.9/max(1,n-1)
            items.append((panel("seam_"+str(i),(x*.025,y*.95,z*.35),level),(off,y*.025,-z*.325)))
        return combine(id,items)
    if name=="utility_cart" and id.startswith("wheel_"):
        # Axis along X, not vertical. Closed revolved visual tire profile.
        profile=((0,0),(z*.31,0),(z*.43,x*.07),(z*.5,x*.22),(z*.5,x*.78),(z*.43,x*.93),(z*.31,x),(0,x))
        mesh=PythonBackend().build(Revolution(id,profile,(48,24,12)[level]))
        return MeshSpec(id,tuple((v[1]-x/2,y/2-v[0],v[2]) for v in mesh.vertices),mesh.triangles)
    return None
