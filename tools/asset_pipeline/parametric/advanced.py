"""Solid recipes for simple profiles in canonical metres, Y-up."""
from dataclasses import dataclass
import math
from .model import MeshSpec, number, vector, stable_id, require

def orient(a,b,c):
    return (b[0]-a[0])*(c[1]-a[1])-(b[1]-a[1])*(c[0]-a[0])

def signed_area(p):
    return sum(orient(p[0],p[i],p[i+1]) for i in range(1,len(p)-1))/2

def _on(a,b,p,eps,linear):
    return abs(orient(a,b,p))<=eps and all(min(a[i],b[i])-linear<=p[i]<=max(a[i],b[i])+linear for i in range(2))

def _intersects(a,b,c,d,eps,linear):
    x,y,z,w=orient(a,b,c),orient(a,b,d),orient(c,d,a),orient(c,d,b)
    if ((x>eps and y< -eps) or (y>eps and x< -eps)) and ((z>eps and w< -eps) or (w>eps and z< -eps)):
        return True
    return any((_on(a,b,c,eps,linear),_on(a,b,d,eps,linear),_on(c,d,a,eps,linear),_on(c,d,b,eps,linear)))

def _profile(raw):
    p=tuple(vector(v,2) for v in raw)
    n=len(p)
    require(3<=n<=256 and len(set(p))==n,"profile needs 3..256 unique vertices; closure implicit")
    extent=max(max(v[i] for v in p)-min(v[i] for v in p) for i in range(2))
    require(math.isfinite(extent) and 0<extent<=1e6,"invalid extent")
    eps=max(extent**2*1e-12,1e-12)
    linear=max(extent*1e-12,1e-12)
    for i in range(n):
        require(abs(orient(p[i-1],p[i],p[(i+1)%n]))>eps,"collinear or degenerate corner")
        for j in range(i+1,n):
            if j==i+1 or (i==0 and j==n-1):
                continue
            require(not _intersects(p[i],p[(i+1)%n],p[j],p[(j+1)%n],eps,linear),"self-intersecting profile")
    area=signed_area(p)
    require(math.isfinite(area) and abs(area)>eps,"zero area")
    if area<0:
        p=p[::-1]
    start=min(range(n),key=p.__getitem__)
    return p[start:]+p[:start],eps

def triangulate_profile(points):
    p,eps=_profile(points)
    remaining=list(range(len(p)))
    faces=[]
    while len(remaining)>3:
        for k,i in enumerate(remaining):
            a,b,c=remaining[k-1],i,remaining[(k+1)%len(remaining)]
            if orient(p[a],p[b],p[c])<=eps:
                continue
            if any(all(orient(p[u],p[v],p[j])>=-eps for u,v in ((a,b),(b,c),(c,a)))
                   for j in remaining if j not in (a,b,c)):
                continue
            faces.append((a,b,c))
            del remaining[k]
            break
        else:
            raise ValueError("cannot triangulate profile robustly")
    faces.append(tuple(remaining))
    require(all(orient(p[a],p[b],p[c])>eps for a,b,c in faces),"degenerate cap")
    require(math.isclose(sum(orient(p[a],p[b],p[c])/2 for a,b,c in faces),
                         signed_area(p),rel_tol=1e-9,abs_tol=eps),"cap area mismatch")
    return p,tuple(faces)

@dataclass(frozen=True)
class Extrusion:
    id: str
    profile_xz: tuple
    height_m: float
    y_min_m: float=0.

    def __post_init__(self):
        stable_id(self.id)
        p,_=triangulate_profile(self.profile_xz)
        h,y=number(self.height_m),number(self.y_min_m)
        require(h>0 and math.isfinite(y+h) and y+h>y,"invalid extrusion height")
        object.__setattr__(self,"profile_xz",p)
        object.__setattr__(self,"height_m",h)
        object.__setattr__(self,"y_min_m",y)

@dataclass(frozen=True)
class Revolution:
    id: str
    profile_ry: tuple
    segments: int=64

    def __post_init__(self):
        stable_id(self.id)
        p,_=_profile(self.profile_ry)
        require(all(r>=0 for r,y in p),"negative radius")
        axis=[i for i,(r,y) in enumerate(p) if r==0]
        require(len(axis)<=2,"at most two axis vertices")
        require(len(axis)!=2 or axis[1]-axis[0] in (1,len(p)-1),"axis vertices must be adjacent")
        require(type(self.segments) is int and 3<=self.segments<=512,"segments out of range")
        require(len(p)*self.segments<=65536,"vertex budget exceeded")
        object.__setattr__(self,"profile_ry",p)

def build_advanced(recipe):
    if isinstance(recipe,Extrusion):
        p,cap=triangulate_profile(recipe.profile_xz)
        n=len(p)
        vs=[(x,y,z) for y in (recipe.y_min_m,recipe.y_min_m+recipe.height_m) for x,z in p]
        fs=list(cap)+[(a+n,c+n,b+n) for a,b,c in cap]
        for i in range(n):
            j=(i+1)%n
            fs.extend(((i,i+n,j+n),(i,j+n,j)))
    elif isinstance(recipe,Revolution):
        n=recipe.segments
        vs=[]
        rings=[]
        for radius,y in recipe.profile_ry:
            start=len(vs)
            if radius==0:
                vs.append((0,y,0))
                rings.append([start]*n)
            else:
                vs.extend((radius*math.cos(math.tau*i/n),y,radius*math.sin(math.tau*i/n)) for i in range(n))
                rings.append(list(range(start,start+n)))
        fs=[]
        for k,a in enumerate(rings):
            b=rings[(k+1)%len(rings)]
            for i in range(n):
                j=(i+1)%n
                for f in ((a[i],b[i],b[j]),(a[i],b[j],a[j])):
                    if len(set(f))==3:
                        fs.append(f)
    else:
        raise TypeError("unsupported advanced recipe")
    mesh=MeshSpec(recipe.id,vs,fs)
    require(mesh.closed_oriented() and mesh.signed_volume()>0,"invalid generated solid")
    return mesh
