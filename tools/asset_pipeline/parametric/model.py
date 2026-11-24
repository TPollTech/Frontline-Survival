"""Immutable geometry/scene IR. Metres, RH, Y-up, column-major affine transforms."""
from __future__ import annotations
from dataclasses import dataclass, field, asdict
import hashlib
import json
import math
import re

def require(condition, message):
    if not condition:
        raise ValueError(message)

def number(v):
    require(type(v) in (int, float) and math.isfinite(v), "expected finite number")
    return float(v) if v else 0.0

def vector(values, size):
    out = tuple(number(v) for v in values)
    require(len(out) == size, f"expected {size} components")
    return out

def stable_id(value):
    require(isinstance(value, str) and re.fullmatch(r"[a-z][a-z0-9_:-]*", value) is not None, "invalid stable ID")
    return value

def sub(a, b):
    return tuple(x-y for x,y in zip(a,b))

def cross(a, b):
    return (a[1]*b[2]-a[2]*b[1], a[2]*b[0]-a[0]*b[2], a[0]*b[1]-a[1]*b[0])

def dot(a,b):
    return sum(x*y for x,y in zip(a,b))

def canonical_to_blender(v):
    x,y,z = vector(v,3)
    return (x,-z,y)

def blender_to_canonical(v):
    x,y,z = vector(v,3)
    return (x,z,-y)

@dataclass(frozen=True)
class Transform:
    matrix: tuple = (1.,0.,0.,0., 0.,1.,0.,0., 0.,0.,1.,0., 0.,0.,0.,1.)

    def __post_init__(self):
        m = vector(self.matrix,16)
        require((m[3],m[7],m[11],m[15]) == (0.,0.,0.,1.), "not affine")
        determinant = dot(m[:3], cross(m[4:7],m[8:11]))
        require(math.isfinite(determinant) and determinant > 1e-12, "singular or reflected basis")
        object.__setattr__(self,"matrix",m)

    @classmethod
    def translation(cls, xyz):
        x,y,z = vector(xyz,3)
        return cls((1,0,0,0,0,1,0,0,0,0,1,0,x,y,z,1))

    @classmethod
    def scale(cls, xyz):
        x,y,z = vector(xyz,3)
        require(min(x,y,z)>0, "positive scale required")
        return cls((x,0,0,0,0,y,0,0,0,0,z,0,0,0,0,1))

    def __matmul__(self, other):
        a,b = self.matrix,other.matrix
        return Transform(tuple(sum(a[k*4+r]*b[c*4+k] for k in range(4)) for c in range(4) for r in range(4)))

    def point(self, value):
        v = vector(value,3)+(1.,)
        m = self.matrix
        return tuple(sum(m[c*4+r]*v[c] for c in range(4)) for r in range(3))

@dataclass(frozen=True)
class MeshSpec:
    id: str
    vertices: tuple
    triangles: tuple

    def __post_init__(self):
        stable_id(self.id)
        vs=tuple(vector(v,3) for v in self.vertices)
        fs=tuple(tuple(f) for f in self.triangles)
        require(bool(vs) and bool(fs), "empty mesh")
        seen=set()
        used=set()
        for f in fs:
            require(len(f)==3 and all(type(i) is int and 0<=i<len(vs) for i in f), "bad triangle index")
            require(len(set(f))==3, "repeated index")
            key=tuple(sorted(f))
            require(key not in seen, "duplicate triangle")
            seen.add(key)
            used.update(f)
            a,b,c=(vs[i] for i in f)
            n=cross(sub(b,a),sub(c,a))
            area2=dot(n,n)
            require(math.isfinite(area2) and area2>1e-24, "degenerate triangle")
        require(len(used)==len(vs), "unused vertices")
        object.__setattr__(self,"vertices",vs)
        object.__setattr__(self,"triangles",fs)

    def bounds(self):
        return bounds(self.vertices)

    def signed_volume(self):
        # Only meaningful for closed consistently oriented meshes.
        return sum(dot(self.vertices[a],cross(self.vertices[b],self.vertices[c])) for a,b,c in self.triangles)/6

    def closed_oriented(self):
        edges={}
        for a,b,c in self.triangles:
            for u,v in ((a,b),(b,c),(c,a)):
                key=min(u,v),max(u,v)
                count, balance=edges.get(key,(0,0))
                edges[key]=(count+1,balance+(1 if u<v else -1))
        return all(count==2 and balance==0 for count,balance in edges.values())

def bounds(vertices):
    vs=tuple(vertices)
    require(bool(vs),"no points for bounds")
    return (tuple(min(v[i] for v in vs) for i in range(3)),tuple(max(v[i] for v in vs) for i in range(3)))

@dataclass(frozen=True)
class MaterialSpec:
    id: str
    base_color: tuple = (0.5,0.5,0.5,1.)
    metallic: float = 0.
    roughness: float = 0.5

    def __post_init__(self):
        stable_id(self.id)
        color=vector(self.base_color,4)
        metallic=number(self.metallic)
        roughness=number(self.roughness)
        require(all(0<=x<=1 for x in (*color,metallic,roughness)), "material range")
        object.__setattr__(self,"base_color",color)
        object.__setattr__(self,"metallic",metallic)
        object.__setattr__(self,"roughness",roughness)

@dataclass(frozen=True)
class NodeSpec:
    id: str
    mesh_id: str | None = None
    parent_id: str | None = None
    material_id: str | None = None
    local: Transform = field(default_factory=Transform)

    def __post_init__(self):
        stable_id(self.id)
        for x in (self.mesh_id,self.parent_id,self.material_id):
            if x is not None:
                stable_id(x)
        require(isinstance(self.local,Transform),"expected transform")
        require(self.mesh_id is not None or self.material_id is None,"material requires mesh")

@dataclass(frozen=True)
class SceneSpec:
    id: str
    meshes: tuple
    materials: tuple
    nodes: tuple

    def __post_init__(self):
        stable_id(self.id)
        for key,cls in (("meshes",MeshSpec),("materials",MaterialSpec),("nodes",NodeSpec)):
            items=tuple(getattr(self,key))
            require(all(isinstance(x,cls) for x in items),"wrong IR item: "+key)
            require(len({x.id for x in items})==len(items),"duplicate ID: "+key)
            object.__setattr__(self,key,tuple(sorted(items,key=lambda x:x.id)))
        mesh_ids={x.id for x in self.meshes}
        mat_ids={x.id for x in self.materials}
        nodes={x.id:x for x in self.nodes}
        require(bool(nodes),"empty scene")
        for n in self.nodes:
            require(n.mesh_id is None or n.mesh_id in mesh_ids,"missing mesh")
            require(n.material_id is None or n.material_id in mat_ids,"missing material")
            require(n.parent_id is None or n.parent_id in nodes,"missing parent")
        self.world_transforms()

    def world_transforms(self):
        nodes={x.id:x for x in self.nodes}
        done={}
        for key in nodes:
            chain=[]
            active=set()
            current=key
            while current is not None and current not in done:
                require(current not in active,"hierarchy cycle")
                active.add(current)
                chain.append(current)
                current=nodes[current].parent_id
            world=done[current] if current is not None else Transform()
            for item in reversed(chain):
                world=world@nodes[item].local
                done[item]=world
        return done

    def world_bounds(self):
        transforms=self.world_transforms()
        meshes={x.id:x for x in self.meshes}
        return bounds(transforms[n.id].point(v) for n in self.nodes if n.mesh_id is not None for v in meshes[n.mesh_id].vertices)

    def canonical_json(self):
        return json.dumps({"schema_version":1,"unit":"m","up":"+Y","handedness":"right","scene":asdict(self)},sort_keys=True,separators=(",",":"),allow_nan=False)

    def sha256(self):
        return hashlib.sha256(self.canonical_json().encode("utf-8")).hexdigest()
