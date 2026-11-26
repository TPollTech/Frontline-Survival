"""Neutral parametric curves, surface patches, lofts and authored topology.

Coordinates are canonical metres, +Y up. No scene or production asset mutation.
"""
from dataclasses import dataclass
from collections import defaultdict
import math
from .model import MeshSpec, number, vector, require, stable_id, sub, cross, dot

def _count(value,low,high):
    require(type(value) is int and low<=value<=high,"subdivision count out of range")
    return value

def _t(value):
    t=number(value)
    require(0<=t<=1,"parameter outside [0,1]")
    return t

def _blend(a,b,t):
    return tuple(x+(y-x)*t for x,y in zip(a,b))

def _casteljau(points,t):
    p=list(points)
    while len(p)>1:
        p=[_blend(a,b,t) for a,b in zip(p,p[1:])]
    return p[0]

@dataclass(frozen=True)
class BezierCurve:
    """Piecewise cubic Bezier; shared endpoint and optional C1 continuity."""
    segments: tuple
    require_c1: bool=False

    def __post_init__(self):
        segments=tuple(tuple(vector(p,3) for p in s) for s in self.segments)
        require(1<=len(segments)<=128 and all(len(s)==4 for s in segments),"expected cubic segments")
        require(type(self.require_c1) is bool,"require_c1 must be bool")
        for a,b in zip(segments,segments[1:]):
            require(a[-1]==b[0],"disconnected curve")
            if self.require_c1:
                require(all(math.isclose(x,y,rel_tol=1e-9,abs_tol=1e-10)
                            for x,y in zip(sub(a[3],a[2]),sub(b[1],b[0]))),"non-C1 join")
        object.__setattr__(self,"segments",segments)

    def point(self,index,t):
        require(type(index) is int and 0<=index<len(self.segments),"segment index")
        return _casteljau(self.segments[index],_t(t))

    def tangent(self,index,t):
        require(type(index) is int and 0<=index<len(self.segments),"segment index")
        p=self.segments[index]
        return _casteljau([tuple(3*x for x in sub(b,a)) for a,b in zip(p,p[1:])],_t(t))

    def sample(self,steps=16):
        _count(steps,1,512)
        require(len(self.segments)*steps<=65536,"curve sampling budget")
        return tuple(self.point(k,i/steps) for k in range(len(self.segments))
                     for i in range(steps))+ (self.segments[-1][-1],)

@dataclass(frozen=True)
class BezierPatch:
    """Tensor-product bicubic patch; u along rows, v along columns."""
    id: str
    control: tuple
    u_steps: int=16
    v_steps: int=16

    def __post_init__(self):
        stable_id(self.id)
        p=tuple(tuple(vector(v,3) for v in row) for row in self.control)
        require(len(p)==4 and all(len(row)==4 for row in p),"expected 4x4 patch")
        _count(self.u_steps,1,256)
        _count(self.v_steps,1,256)
        require((self.u_steps+1)*(self.v_steps+1)<=65536,"patch vertex budget")
        object.__setattr__(self,"control",p)

    def point(self,u,v):
        u,v=_t(u),_t(v)
        return _casteljau([_casteljau(row,v) for row in self.control],u)

@dataclass(frozen=True)
class LoftSection:
    y_m: float
    center_xz: tuple
    radii_xz: tuple
    twist_rad: float=0.

    def __post_init__(self):
        object.__setattr__(self,"y_m",number(self.y_m))
        object.__setattr__(self,"center_xz",vector(self.center_xz,2))
        r=vector(self.radii_xz,2)
        require(min(r)>0,"loft radius must be positive")
        object.__setattr__(self,"radii_xz",r)
        object.__setattr__(self,"twist_rad",number(self.twist_rad))

@dataclass(frozen=True)
class OrganicLoft:
    """Closed loft of superelliptical rings with strictly increasing height.

    Interpolates radii/centres/twist using smoothstep, height linearly.
    Seam shares vertex indices; end caps are explicit. ``section_power`` is the
    superellipse exponent: 2 is a true ellipse (organic forms) and values up to
    16 approach a rounded rectangle with flat sides and filleted corners, which
    is what machined or moulded furniture needs without faking it per part.
    """
    id: str
    sections: tuple
    radial_segments: int=32
    steps_per_interval: int=8
    section_power: float=2.0

    def __post_init__(self):
        stable_id(self.id)
        s=tuple(self.sections)
        require(2<=len(s)<=128 and all(isinstance(x,LoftSection) for x in s),"expected loft sections")
        require(all(b.y_m>a.y_m for a,b in zip(s,s[1:])),"height must increase strictly")
        _count(self.radial_segments,3,512)
        _count(self.steps_per_interval,1,256)
        power=number(self.section_power)
        require(2<=power<=16,"section power outside [2,16]")
        object.__setattr__(self,"section_power",power)
        require(((len(s)-1)*self.steps_per_interval+1)*self.radial_segments+2<=65536,"loft vertex budget")
        object.__setattr__(self,"sections",s)

@dataclass(frozen=True)
class CustomTopology:
    """Explicit authored triangle/quad indices, with manifold vertex-link checks."""
    id: str
    vertices: tuple
    faces: tuple
    closed: bool=False

    def __post_init__(self):
        stable_id(self.id)
        v=tuple(vector(p,3) for p in self.vertices)
        f=tuple(tuple(p) for p in self.faces)
        require(type(self.closed) is bool,"closed must be bool")
        require(3<=len(v)<=65536 and 1<=len(f)<=131072,"custom topology budget")
        require(all(len(p) in (3,4) and len(set(p))==len(p) and
                    all(type(i) is int and 0<=i<len(v) for i in p) for p in f),"invalid face")
        object.__setattr__(self,"vertices",v)
        object.__setattr__(self,"faces",f)

def _topology(mesh,closed):
    """Reject branching edges, inconsistent winding and disconnected vertex fans."""
    edges=defaultdict(list)
    links=defaultdict(list)
    for a,b,c in mesh.triangles:
        for u,v,w in ((a,b,c),(b,c,a),(c,a,b)):
            edges[min(u,v),max(u,v)].append((u,v))
            links[u].append((v,w))
    for pair in edges.values():
        require(len(pair)<=2 and (len(pair)!=2 or pair[0]==pair[1][::-1]),"nonmanifold or misoriented edge")
        require(not closed or len(pair)==2,"open boundary")
    for pairs in links.values():
        graph=defaultdict(set)
        for a,b in pairs:
            graph[a].add(b)
            graph[b].add(a)
        require(all(1<=len(n)<=2 for n in graph.values()),"branched vertex fan")
        ends=sum(len(n)==1 for n in graph.values())
        require(ends in ((0,) if closed else (0,2)),"invalid vertex fan boundary")
        seen=set()
        stack=[next(iter(graph))]
        while stack:
            n=stack.pop()
            if n not in seen:
                seen.add(n)
                stack.extend(graph[n]-seen)
        require(len(seen)==len(graph),"disconnected vertex fan")
    if closed:
        require(mesh.closed_oriented() and mesh.signed_volume()>0,"invalid closed solid")
    return mesh

def build_organic(recipe):
    if isinstance(recipe,BezierPatch):
        nu,nv=recipe.u_steps,recipe.v_steps
        vs=[recipe.point(i/nu,j/nv) for i in range(nu+1) for j in range(nv+1)]
        fs=[]
        for i in range(nu):
            for j in range(nv):
                a=i*(nv+1)+j
                b=a+nv+1
                fs.extend(((a,b,b+1),(a,b+1,a+1)))
        return _topology(MeshSpec(recipe.id,vs,fs),False)
    if isinstance(recipe,OrganicLoft):
        sections=recipe.sections
        n=recipe.radial_segments
        k=recipe.steps_per_interval
        rings=[]
        for a,b in zip(sections,sections[1:]):
            for j in range(k):
                t=j/k
                s=t*t*(3-2*t)
                rings.append(LoftSection(a.y_m+(b.y_m-a.y_m)*t,
                    _blend(a.center_xz,b.center_xz,s),_blend(a.radii_xz,b.radii_xz,s),
                    a.twist_rad+(b.twist_rad-a.twist_rad)*s))
        rings.append(sections[-1])
        vs=[]
        # Superellipse exponent: 2 keeps the historical elliptical ring exactly.
        e=2.0/recipe.section_power
        for ring in rings:
            c,s=math.cos(ring.twist_rad),math.sin(ring.twist_rad)
            for i in range(n):
                a=math.tau*i/n
                ca,sa=math.cos(a),math.sin(a)
                x=ring.radii_xz[0]*math.copysign(abs(ca)**e,ca)
                z=ring.radii_xz[1]*math.copysign(abs(sa)**e,sa)
                vs.append((ring.center_xz[0]+c*x-s*z,ring.y_m,ring.center_xz[1]+s*x+c*z))
        fs=[]
        for j in range(len(rings)-1):
            for i in range(n):
                a=j*n+i
                b=j*n+(i+1)%n
                fs.extend(((a,a+n,b+n),(a,b+n,b)))
        bottom,top=len(vs),len(vs)+1
        for ring in (rings[0],rings[-1]):
            vs.append((ring.center_xz[0],ring.y_m,ring.center_xz[1]))
        last=(len(rings)-1)*n
        for i in range(n):
            j=(i+1)%n
            fs.extend(((bottom,i,j),(top,last+j,last+i)))
        return _topology(MeshSpec(recipe.id,vs,fs),True)
    if isinstance(recipe,CustomTopology):
        fs=[]
        for f in recipe.faces:
            if len(f)==3:
                fs.append(f)
                continue
            a,b,c,d=f
            v=recipe.vertices
            n=cross(sub(v[b],v[a]),sub(v[c],v[a]))
            m=cross(sub(v[c],v[a]),sub(v[d],v[a]))
            require(dot(n,m)>0,"folded or concave quad; author explicit triangles")
            # Require all four corner turns to agree, ruling out bowties.
            for i in range(4):
                p,q,r=(v[f[(i+j)%4]] for j in range(3))
                require(dot(cross(sub(q,p),sub(r,q)),n)>0,"nonconvex quad")
            fs.extend(((a,b,c),(a,c,d)))
        return _topology(MeshSpec(recipe.id,recipe.vertices,fs),recipe.closed)
    raise TypeError("unsupported organic recipe")
