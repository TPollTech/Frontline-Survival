"""Independent collider IR and deterministic authored/parametric LODs.
Budgets are provisional per asset instance, not measured performance targets.
"""
from dataclasses import dataclass, field, replace, asdict
import hashlib
import json
import math
from .model import MeshSpec, SceneSpec, Transform, stable_id, require, vector, number, cross, dot, sub, bounds
from .rig import rigid
from .recipes import PythonBackend, Cylinder
from .advanced import Revolution
from .organic import BezierPatch, OrganicLoft

@dataclass(frozen=True)
class CategoryBudget:
    triangles: tuple
    max_colliders: int
    max_collision_triangles: int
    max_material_slots: int

    def __post_init__(self):
        t=tuple(self.triangles)
        require(len(t)==3 and all(type(x) is int and x>0 for x in t)
                and t[0]>=t[1]>=t[2],"invalid LOD budgets")
        require(all(type(x) is int and x>0 for x in (self.max_colliders,self.max_collision_triangles,self.max_material_slots)),"invalid budget")
        object.__setattr__(self,"triangles",t)

# Caps per asset instance (maps/terrain must be partitioned into chunks).
# Categories from historical catalog that carry visible geometry are covered.
BUDGETS={
    "weapon":CategoryBudget((18000,7000,1800),8,256,8),
    "accessory":CategoryBudget((6000,2400,600),4,128,4),
    "first_person":CategoryBudget((24000,10000,3000),12,512,8),
    "character":CategoryBudget((22000,8000,2200),16,512,8),
    "object":CategoryBudget((8000,2800,700),8,256,4),
    "environment":CategoryBudget((12000,4000,1000),12,512,6),
    "vehicle":CategoryBudget((30000,12000,3000),16,768,8),
    "structure":CategoryBudget((20000,8000,2000),24,2048,8),
    "terrain":CategoryBudget((16000,6000,1500),8,4096,4),
    "map":CategoryBudget((24000,9000,2500),32,8192,12),
    "effect":CategoryBudget((2000,800,200),2,128,2),
    "collision":CategoryBudget((2000,800,200),32,8192,2),
    "geometry_library":CategoryBudget((24000,9000,2500),16,1024,8),
}
NON_GEOMETRY_CATEGORIES=frozenset(("audio","camera","shader","material","physics_query","texture"))

def _convex(mesh):
    require(len(mesh.vertices)<=256 and len(mesh.triangles)<=512,"convex proxy too complex")
    require(mesh.closed_oriented() and mesh.signed_volume()>0,"convex proxy must be closed outward")
    lo,hi=mesh.bounds()
    eps=max(1e-9,max(b-a for a,b in zip(lo,hi))*1e-7)
    for a,b,c in mesh.triangles:
        p,q,r=(mesh.vertices[i] for i in (a,b,c))
        n=cross(sub(q,p),sub(r,p))
        length=math.sqrt(dot(n,n))
        require(all(dot(n,sub(v,p))<=eps*length for v in mesh.vertices),"nonconvex proxy")

@dataclass(frozen=True)
class ColliderSpec:
    id: str
    owner_node_id: str
    kind: str
    local: Transform=field(default_factory=Transform)
    dimensions_m: tuple=()
    proxy: MeshSpec | None=None
    body: str="static"
    layer: int=1
    mask: int=1

    def __post_init__(self):
        stable_id(self.id)
        stable_id(self.owner_node_id)
        rigid(self.local)
        require(self.kind in ("box","sphere","capsule","convex","concave"),"unknown collision shape")
        require(self.body in ("static","dynamic","kinematic"),"unknown body type")
        require(all(type(x) is int and 0<=x<=0xffffffff for x in (self.layer,self.mask)),"invalid collision bits")
        dims=tuple(number(x) for x in self.dimensions_m)
        if self.kind in ("convex","concave"):
            require(not dims and isinstance(self.proxy,MeshSpec),"mesh collider requires independent proxy")
            if self.kind=="convex":
                _convex(self.proxy)
            else:
                require(self.body=="static","concave collision is static only")
        else:
            require(self.proxy is None and len(dims)=={"box":3,"sphere":1,"capsule":2}[self.kind] and all(x>0 for x in dims),"invalid primitive dimensions")
            if self.kind=="capsule":
                require(dims[1]>=2*dims[0],"capsule total height must include both hemispheres")
        object.__setattr__(self,"dimensions_m",dims)

    def triangle_count(self):
        return len(self.proxy.triangles) if self.proxy else 0

    def local_bounds(self):
        if self.proxy:
            return self.proxy.bounds()
        if self.kind=="box":
            half=tuple(x/2 for x in self.dimensions_m)
        elif self.kind=="sphere":
            half=(self.dimensions_m[0],)*3
        else:
            r,h=self.dimensions_m
            half=(r,h/2,r)
        return tuple(-v for v in half),half

@dataclass(frozen=True)
class LODLevel:
    index: int
    start_distance_m: float
    scene: SceneSpec

    def __post_init__(self):
        require(type(self.index) is int and 0<=self.index<=2,"invalid LOD index")
        d=number(self.start_distance_m)
        require(d>=0 and isinstance(self.scene,SceneSpec),"invalid LOD")
        object.__setattr__(self,"start_distance_m",d)

    def metrics(self):
        meshes={m.id:m for m in self.scene.meshes}
        nodes=[n for n in self.scene.nodes if n.mesh_id is not None]
        count=sum(len(meshes[n.mesh_id].triangles) for n in nodes)
        return {"triangles":count,"source_vertices":sum(len(meshes[n.mesh_id].vertices) for n in nodes),
                "render_vertex_upper_bound":count*3,"material_slots":len(nodes)}

@dataclass(frozen=True)
class AssetLOD:
    id: str
    category: str
    levels: tuple
    colliders: tuple=()
    bounds_tolerance: float=0.05
    hysteresis_m: float=1.

    def __post_init__(self):
        stable_id(self.id)
        require(self.category in BUDGETS,"no geometric budget for category")
        levels=tuple(self.levels)
        require(len(levels)==3 and all(isinstance(l,LODLevel) for l in levels),"three LOD levels required")
        levels=tuple(sorted(levels,key=lambda l:l.index))
        require(tuple(l.index for l in levels)==(0,1,2),"LOD indices must be unique")
        require(levels[0].start_distance_m==0 and all(b.start_distance_m>a.start_distance_m for a,b in zip(levels,levels[1:])),"invalid LOD distances")
        tol,h=number(self.bounds_tolerance),number(self.hysteresis_m)
        require(0<=tol<=0.1 and 0<=h<min(b.start_distance_m-a.start_distance_m for a,b in zip(levels,levels[1:]))/2,"invalid LOD tolerances")
        budget=BUDGETS[self.category]
        base=levels[0].scene
        nodes={n.id:n for n in base.nodes}
        reference=base.world_bounds()
        prev=None
        # Keep transforms, pivots, hierarchy and material assignment invariant.
        signature=lambda s:tuple((n.id,n.parent_id,n.material_id,n.local,n.mesh_id is not None) for n in s.nodes)
        for level in levels:
            require(signature(level.scene)==signature(base) and level.scene.materials==base.materials,"LOD hierarchy/material mismatch")
            metrics=level.metrics()
            require(metrics["triangles"]<=budget.triangles[level.index] and metrics["material_slots"]<=budget.max_material_slots,"visual budget exceeded")
            require(metrics["triangles"]>0 and (prev is None or metrics["triangles"]<prev),"LOD triangle count must strictly decrease")
            prev=metrics["triangles"]
            # Bound each node independently, not only the asset AABB.
            ref_mesh={m.id:m for m in base.meshes}
            actual_mesh={m.id:m for m in level.scene.meshes}
            for a,n in zip(base.nodes,level.scene.nodes):
                if a.mesh_id is None:
                    continue
                expected=ref_mesh[a.mesh_id].bounds()
                actual=actual_mesh[n.mesh_id].bounds()
                allowed=tuple(max(1e-7,(b-a)*tol) for a,b in zip(*expected))
                require(all(abs(x-y)<=d for u,v in zip(expected,actual) for x,y,d in zip(u,v,allowed)),"LOD local bounds drift")
            allowed=tuple(max(1e-7,(b-a)*tol) for a,b in zip(*reference))
            require(all(abs(x-y)<=d for u,v in zip(reference,level.scene.world_bounds()) for x,y,d in zip(u,v,allowed)),"LOD world bounds drift")
        colliders=tuple(self.colliders)
        require(all(isinstance(c,ColliderSpec) for c in colliders) and len({c.id for c in colliders})==len(colliders),"invalid/duplicate collider")
        require(len(colliders)<=budget.max_colliders and sum(c.triangle_count() for c in colliders)<=budget.max_collision_triangles,"collision budget exceeded")
        visual_ids={m.id for l in levels for m in l.scene.meshes}
        visual_meshes=[m for l in levels for m in l.scene.meshes]
        for c in colliders:
            require(c.owner_node_id in nodes,"missing collider owner")
            rigid(base.world_transforms()[c.owner_node_id])
            if c.proxy:
                require(c.proxy.id not in visual_ids and not any(c.proxy.vertices==m.vertices and c.proxy.triangles==m.triangles for m in visual_meshes),"collision proxy must be independent of visual mesh")
        object.__setattr__(self,"levels",levels)
        object.__setattr__(self,"colliders",tuple(sorted(colliders,key=lambda c:c.id)))
        object.__setattr__(self,"bounds_tolerance",tol)
        object.__setattr__(self,"hysteresis_m",h)

    def select(self,distance_m,previous=None):
        d=number(distance_m)
        require(d>=0,"negative LOD distance")
        if previous is None:
            return max(l.index for l in self.levels if d>=l.start_distance_m)
        require(type(previous) is int and 0<=previous<=2,"invalid previous LOD")
        i=previous
        while i<2 and d>=self.levels[i+1].start_distance_m+self.hysteresis_m:
            i+=1
        while i>0 and d<self.levels[i].start_distance_m-self.hysteresis_m:
            i-=1
        return i

    def collision_world(self,id):
        c=next((c for c in self.colliders if c.id==id),None)
        require(c is not None,"unknown collider")
        return self.levels[0].scene.world_transforms()[c.owner_node_id]@c.local

    def canonical_json(self):
        return json.dumps({"schema_version":1,"unit":"m","asset":asdict(self)},sort_keys=True,separators=(",",":"),allow_nan=False)

    def sha256(self):
        return hashlib.sha256(self.canonical_json().encode()).hexdigest()

def resample_recipe(recipe,index):
    """Rebuild from canonical source rather than arbitrarily decimating UVs/skin.
    Only recipes with explicit sampling supported. Artist-authored LODs otherwise.
    """
    require(type(index) is int and 0<=index<=2,"invalid LOD index")
    if index==0:
        return recipe
    divisor=2**index
    def reduced(n,minimum):
        return max(minimum,n//divisor)
    id=recipe.id+f":lod{index}"
    if isinstance(recipe,(Cylinder,Revolution)):
        return replace(recipe,id=id,segments=reduced(recipe.segments,8))
    if isinstance(recipe,OrganicLoft):
        return replace(recipe,id=id,radial_segments=reduced(recipe.radial_segments,8),
                       steps_per_interval=reduced(recipe.steps_per_interval,1))
    if isinstance(recipe,BezierPatch):
        return replace(recipe,id=id,u_steps=reduced(recipe.u_steps,1),v_steps=reduced(recipe.v_steps,1))
    raise ValueError("recipe requires authored LODs")

def build_single_recipe_lods(recipe,category,*,distances=(0,12,30),colliders=()):
    require(len(distances)==3,"three distances required")
    levels=[]
    for i,d in enumerate(distances):
        mesh=PythonBackend().build(resample_recipe(recipe,i))
        from .model import NodeSpec
        scene=SceneSpec(recipe.id,(mesh,),(),(NodeSpec("root",mesh.id),))
        levels.append(LODLevel(i,d,scene))
    return AssetLOD(recipe.id,category,levels,colliders)
