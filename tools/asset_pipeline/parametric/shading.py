"""Corner attributes and indexed render buffers, independent of topology IR."""
from collections import defaultdict
from dataclasses import dataclass
import math
from .model import MeshSpec, require, vector, number, sub, cross, dot

def norm(v):
    return math.sqrt(dot(v,v))

def unit(v):
    n=norm(v)
    require(math.isfinite(n) and n>1e-15,"zero or nonfinite direction")
    return tuple(x/n for x in v)

def scale(v,s):
    return tuple(x*s for x in v)

def add(a,b):
    return tuple(x+y for x,y in zip(a,b))

def angle(a,b):
    return math.atan2(norm(cross(a,b)),dot(a,b))

def face_data(mesh):
    for a,b,c in mesh.triangles:
        p,q,r=(mesh.vertices[i] for i in (a,b,c))
        n=cross(sub(q,p),sub(r,p))
        yield unit(n),norm(n)/2,(
            angle(sub(q,p),sub(r,p)),angle(sub(r,q),sub(p,q)),angle(sub(p,r),sub(q,r)))

def corner_normals(mesh, *, weighting="area_angle", crease_rad=math.pi/3, sharp_edges=()):
    """Average connected incident faces, split across hard or boundary edges."""
    require(isinstance(mesh,MeshSpec),"expected MeshSpec")
    require(weighting in ("uniform","area","angle","area_angle"),"invalid normal weighting")
    crease=number(crease_rad)
    require(0<=crease<=math.pi,"crease outside [0,pi]")
    sharp=set()
    for edge in sharp_edges:
        e=tuple(edge)
        require(len(e)==2 and all(type(i) is int and 0<=i<len(mesh.vertices) for i in e)
                and e[0]!=e[1],"invalid sharp edge")
        sharp.add(tuple(sorted(e)))
    data=list(face_data(mesh))
    edges=defaultdict(list)
    for f,tri in enumerate(mesh.triangles):
        for j in range(3):
            u,v=tri[j],tri[(j+1)%3]
            edges[min(u,v),max(u,v)].append((f,j,u,v))
    require(sharp<=set(edges),"unknown sharp edge")
    parent=list(range(3*len(data)))
    def find(i):
        while parent[i]!=i:
            parent[i]=parent[parent[i]]
            i=parent[i]
        return i
    def join(i,j):
        a,b=find(i),find(j)
        if a!=b:
            parent[max(a,b)]=min(a,b)
    for key,entries in edges.items():
        require(len(entries)<=2,"nonmanifold normal edge")
        if len(entries)!=2:
            continue
        (f,j,u,v),(g,k,w,x)=entries
        require((u,v)==(x,w),"inconsistent winding")
        if key in sharp or crease==0 or dot(data[f][0],data[g][0])<math.cos(crease)-1e-12:
            continue
        join(3*f+j,3*g+(k+1)%3)
        join(3*f+(j+1)%3,3*g+k)
    sums=defaultdict(lambda:(0.,0.,0.))
    for f,(n,area,angles) in enumerate(data):
        for j,a in enumerate(angles):
            w={"uniform":1.,"area":area,"angle":a,"area_angle":area*a}[weighting]
            k=find(3*f+j)
            sums[k]=add(sums[k],scale(n,w))
    normals={k:unit(v) for k,v in sums.items()}
    return tuple(normals[find(i)] for i in range(len(parent)))

def planar_uv(mesh, *, origin=(0,0,0), u_axis=(1,0,0), v_axis=(0,0,1), metres_per_tile=1.):
    """Explicit orthogonal planar projection; tiled coordinates may exceed 0..1."""
    o=vector(origin,3)
    u,v=unit(vector(u_axis,3)),unit(vector(v_axis,3))
    size=number(metres_per_tile)
    require(size>0 and abs(dot(u,v))<1e-8,"invalid planar basis")
    return tuple((dot(sub(mesh.vertices[i],o),u)/size,dot(sub(mesh.vertices[i],o),v)/size)
                 for f in mesh.triangles for i in f)

def triangle_atlas_uv(mesh, *, padding=0.04):
    """Non-overlapping per-triangle charts, deterministic, aspect preserving.
    Padding is fraction of each cell. Not a production unwrap or texel-density optimizer.
    """
    p=number(padding)
    require(0<p<0.25,"padding outside (0,0.25)")
    side=math.ceil(math.sqrt(len(mesh.triangles)))
    result=[]
    for f,tri in enumerate(mesh.triangles):
        a,b,c=(mesh.vertices[i] for i in tri)
        e=sub(b,a)
        length=norm(e)
        u=unit(e)
        x=dot(sub(c,a),u)
        y=norm(cross(u,sub(c,a)))
        lo=min(0.,x)
        width=max(length,x)-lo
        factor=(1-2*p)/max(width,y)
        # Separate grid cells; no sharing between charts.
        col,row=f%side,f//side
        for q,r in ((0.,0.),(length,0.),(x,y)):
            result.append(((col+p+(q-lo)*factor)/side,(row+p+r*factor)/side))
    return tuple(result)

def _frames(mesh,uv):
    uv=tuple(vector(p,2) for p in uv)
    require(len(uv)==3*len(mesh.triangles),"UV corner count mismatch")
    frames=[]
    for i,(a,b,c) in enumerate(mesh.triangles):
        p,q,r=uv[3*i:3*i+3]
        du,dv=sub(q,p),sub(r,p)
        determinant=du[0]*dv[1]-du[1]*dv[0]
        require(abs(determinant)>1e-15,"degenerate UV triangle")
        e,f=sub(mesh.vertices[b],mesh.vertices[a]),sub(mesh.vertices[c],mesh.vertices[a])
        t=scale(sub(scale(e,dv[1]),scale(f,du[1])),1/determinant)
        bit=scale(sub(scale(f,du[0]),scale(e,dv[0])),1/determinant)
        frames.append((t,bit,1 if determinant>0 else -1))
    return uv,frames

def corner_tangents(mesh,normals,uv):
    """Angle-weighted tangent derivatives, Gram-Schmidt, mirrored UV splits.
    Python fallback is not claimed to be reference MikkTSpace.
    """
    ns=tuple(vector(n,3) for n in normals)
    require(len(ns)==3*len(mesh.triangles),"normal corner count mismatch")
    require(all(abs(norm(n)-1)<1e-6 for n in ns),"nonunit normal")
    uv,frames=_frames(mesh,uv)
    sums=defaultdict(lambda:((0.,0.,0.),(0.,0.,0.)))
    keys=[]
    for f,(_,_,angles) in enumerate(face_data(mesh)):
        t,b,sign=frames[f]
        for j,i in enumerate(mesh.triangles[f]):
            k=3*f+j
            key=(i,ns[k],uv[k],sign)
            keys.append(key)
            old_t,old_b=sums[key]
            sums[key]=(add(old_t,scale(unit(t),angles[j])),add(old_b,scale(unit(b),angles[j])))
    result=[]
    for key,n in zip(keys,ns):
        t,b=sums[key]
        t=unit(sub(t,scale(n,dot(n,t))))
        handed=dot(cross(n,t),b)
        require(abs(handed)>1e-10,"ambiguous tangent handedness")
        result.append(t+(1. if handed>0 else -1.,))
    return tuple(result)

@dataclass(frozen=True)
class RenderMesh:
    """Split render vertices; retains mapping to the unsplit source MeshSpec."""
    mesh: MeshSpec
    positions: tuple
    normals: tuple
    uv: tuple
    tangents: tuple
    indices: tuple
    source_vertices: tuple

    def __post_init__(self):
        require(isinstance(self.mesh,MeshSpec),"expected source MeshSpec")
        for field,size in (("positions",3),("normals",3),("uv",2),("tangents",4)):
            object.__setattr__(self,field,tuple(vector(p,size) for p in getattr(self,field)))
        for field in ("indices","source_vertices"):
            object.__setattr__(self,field,tuple(getattr(self,field)))
        count=len(self.positions)
        require(count>0 and all(len(x)==count for x in (self.normals,self.uv,self.tangents,self.source_vertices)),
                "render buffer length mismatch")
        require(len(self.indices)==3*len(self.mesh.triangles) and all(type(i) is int and 0<=i<count for i in self.indices),"bad render indices")
        require(set(self.indices)==set(range(count)),"unused render vertices")
        require(all(type(i) is int and 0<=i<len(self.mesh.vertices) for i in self.source_vertices),"bad source index")
        require(tuple(self.source_vertices[i] for i in self.indices)==tuple(i for f in self.mesh.triangles for i in f),"render topology mismatch")
        for p,n,t,i in zip(self.positions,self.normals,self.tangents,self.source_vertices):
            require(p==self.mesh.vertices[i],"render position mismatch")
            require(abs(norm(n)-1)<1e-5 and abs(norm(t[:3])-1)<1e-5 and abs(dot(n,t[:3]))<1e-5 and t[3] in (-1.,1.),"invalid tangent frame")
        _frames(self.mesh,tuple(self.uv[i] for i in self.indices))

def build_render_mesh(mesh, *, uv=None, weighting="area_angle", crease_rad=math.pi/3,
                      sharp_edges=(), tangent_backend=None):
    """Use Python tangents by default or inject a verified Blender corner tangent backend."""
    ns=corner_normals(mesh,weighting=weighting,crease_rad=crease_rad,sharp_edges=sharp_edges)
    uv=triangle_atlas_uv(mesh) if uv is None else tuple(vector(p,2) for p in uv)
    _frames(mesh,uv)
    ts=corner_tangents(mesh,ns,uv) if tangent_backend is None else tuple(tangent_backend(mesh,ns,uv))
    require(len(ts)==len(ns),"tangent count mismatch")
    lookup={}
    positions,normals,coords,tangents,source,indices=[],[],[],[],[],[]
    for i,(v,n,u,t) in enumerate(zip((i for f in mesh.triangles for i in f),ns,uv,ts)):
        t=vector(t,4)
        key=(v,n,u,t)
        if key not in lookup:
            lookup[key]=len(positions)
            positions.append(mesh.vertices[v])
            normals.append(n)
            coords.append(u)
            tangents.append(t)
            source.append(v)
        indices.append(lookup[key])
    return RenderMesh(mesh,positions,normals,coords,tangents,indices,source)
