"""Canonical local-space hierarchy, rigid bones, sockets and linear blend skinning."""
from dataclasses import dataclass, field, replace, asdict
import math
import json
import hashlib
from .model import Transform, SceneSpec, MeshSpec, stable_id, require, vector, number, dot, cross, sub

def inverse(t):
    """Inverse of a positive-determinant affine Transform (column major)."""
    require(isinstance(t,Transform),"expected transform")
    m=t.matrix
    a,b,c=m[:3],m[4:7],m[8:11]
    det=dot(a,cross(b,c))
    rows=[tuple(x/det for x in v) for v in (cross(b,c),cross(c,a),cross(a,b))]
    p=m[12:15]
    return Transform(tuple(rows[r][j] if r<3 else 0. for j in range(3) for r in range(4))+
                     tuple(-dot(row,p) for row in rows)+(1.,))

def rotation(axis,radians):
    a=vector(axis,3)
    length=math.sqrt(dot(a,a))
    require(length>1e-12,"zero rotation axis")
    x,y,z=(v/length for v in a)
    t=number(radians)
    c,s,k=math.cos(t),math.sin(t),1-math.cos(t)
    return Transform((c+x*x*k,y*x*k+z*s,z*x*k-y*s,0,
                      x*y*k-z*s,c+y*y*k,z*y*k+x*s,0,
                      x*z*k+y*s,y*z*k-x*s,c+z*z*k,0,0,0,0,1))

def around_pivot(delta,pivot):
    p=vector(pivot,3)
    return Transform.translation(p)@delta@Transform.translation(tuple(-x for x in p))

def rigid(t):
    require(isinstance(t,Transform),"expected transform")
    m=t.matrix
    cols=(m[:3],m[4:7],m[8:11])
    require(all(abs(dot(a,b)-(1 if i==j else 0))<1e-7
                for i,a in enumerate(cols) for j,b in enumerate(cols)),"bone transform must be rigid")
    return t

def reparent(scene,node_id,parent_id,*,keep_world=True):
    require(isinstance(scene,SceneSpec),"expected scene")
    nodes={n.id:n for n in scene.nodes}
    require(node_id in nodes and (parent_id is None or parent_id in nodes),"unknown node")
    world=scene.world_transforms()
    local=nodes[node_id].local
    if keep_world:
        local=inverse(world[parent_id])@world[node_id] if parent_id else world[node_id]
    return replace(scene,nodes=tuple(replace(n,parent_id=parent_id,local=local) if n.id==node_id else n for n in scene.nodes))

@dataclass(frozen=True)
class BoneSpec:
    id: str
    parent_id: str | None=None
    rest_local: Transform=field(default_factory=Transform)
    length_m: float=0.1

    def __post_init__(self):
        stable_id(self.id)
        if self.parent_id is not None:
            stable_id(self.parent_id)
        rigid(self.rest_local)
        length=number(self.length_m)
        require(length>1e-6,"bone length must be positive")
        object.__setattr__(self,"length_m",length)

@dataclass(frozen=True)
class SkeletonSpec:
    id: str
    bones: tuple

    def __post_init__(self):
        stable_id(self.id)
        bones=tuple(self.bones)
        require(1<=len(bones)<=256 and all(isinstance(b,BoneSpec) for b in bones),"invalid bones")
        require(len({b.id for b in bones})==len(bones),"duplicate bone")
        by={b.id:b for b in bones}
        require(sum(b.parent_id is None for b in bones)==1,"one skeleton root required")
        require(all(b.parent_id is None or b.parent_id in by for b in bones),"unknown parent bone")
        # Stable parent-first order, reject cycles, independent of input order.
        pending=set(by)
        ordered=[]
        done=set()
        while pending:
            ready=sorted(i for i in pending if by[i].parent_id is None or by[i].parent_id in done)
            require(bool(ready),"bone hierarchy cycle")
            for i in ready:
                ordered.append(by[i])
                done.add(i)
                pending.remove(i)
        object.__setattr__(self,"bones",tuple(ordered))

    def transforms(self,pose=None):
        pose={} if pose is None else dict(pose)
        require(set(pose)<={b.id for b in self.bones},"unknown pose bone")
        result={}
        for b in self.bones:
            local=b.rest_local@rigid(pose.get(b.id,Transform()))
            result[b.id]=result[b.parent_id]@local if b.parent_id else local
        return result

    def inverse_bind(self):
        return {k:inverse(t) for k,t in self.transforms().items()}

@dataclass(frozen=True)
class SocketSpec:
    id: str
    owner_id: str
    owner_kind: str="node"
    local: Transform=field(default_factory=Transform)

    def __post_init__(self):
        stable_id(self.id)
        stable_id(self.owner_id)
        require(self.owner_kind in ("node","bone") and isinstance(self.local,Transform),"invalid socket")

@dataclass(frozen=True)
class SkinSpec:
    """Weights indexed by source vertex. Max four nonzero influences, sum 1."""
    mesh_id: str
    skeleton_id: str
    weights: tuple

    def __post_init__(self):
        stable_id(self.mesh_id)
        stable_id(self.skeleton_id)
        rows=[]
        for row in self.weights:
            entries=tuple((stable_id(b),number(w)) for b,w in row)
            require(1<=len(entries)<=4 and len({b for b,w in entries})==len(entries),"invalid influence count or duplicate")
            require(all(0<w<=1 for b,w in entries) and abs(sum(w for b,w in entries)-1)<1e-8,"weights must sum to one")
            total=sum(w for b,w in entries)
            rows.append(tuple(sorted((b,w/total) for b,w in entries)))
        require(bool(rows),"empty skin")
        object.__setattr__(self,"weights",tuple(rows))

    def validate(self,mesh,skeleton):
        require(isinstance(mesh,MeshSpec) and mesh.id==self.mesh_id,"wrong mesh binding")
        require(isinstance(skeleton,SkeletonSpec) and skeleton.id==self.skeleton_id,"wrong skeleton binding")
        require(len(self.weights)==len(mesh.vertices),"weights count mismatch")
        ids={b.id for b in skeleton.bones}
        require(all(b in ids for row in self.weights for b,w in row),"unknown influence bone")

    def deform(self,mesh,skeleton,pose=None):
        self.validate(mesh,skeleton)
        world=skeleton.transforms(pose)
        bind=skeleton.inverse_bind()
        matrices={k:world[k]@bind[k] for k in world}
        result=[]
        for p,row in zip(mesh.vertices,self.weights):
            points=[(matrices[b].point(p),w) for b,w in row]
            result.append(tuple(sum(v[i]*w for v,w in points) for i in range(3)))
        return tuple(result)

    def render_weights(self,render,skeleton):
        self.validate(render.mesh,skeleton)
        return tuple(self.weights[i] for i in render.source_vertices)

@dataclass(frozen=True)
class RigSpec:
    """One skeleton in scene anchor's local frame, optional skinned meshes/sockets."""
    id: str
    scene: SceneSpec
    skeleton: SkeletonSpec
    anchor_node_id: str
    skins: tuple=()
    sockets: tuple=()

    def __post_init__(self):
        stable_id(self.id)
        require(isinstance(self.scene,SceneSpec) and isinstance(self.skeleton,SkeletonSpec),"invalid rig scene/skeleton")
        nodes={n.id:n for n in self.scene.nodes}
        require(self.anchor_node_id in nodes,"missing rig anchor")
        skins=tuple(self.skins)
        sockets=tuple(self.sockets)
        require(all(isinstance(s,SkinSpec) for s in skins) and len({s.mesh_id for s in skins})==len(skins),"duplicate or invalid skin")
        require(all(isinstance(s,SocketSpec) for s in sockets) and len({s.id for s in sockets})==len(sockets),"duplicate or invalid socket")
        meshes={m.id:m for m in self.scene.meshes}
        world=self.scene.world_transforms()
        anchor=world[self.anchor_node_id]
        for skin in skins:
            require(skin.mesh_id in meshes,"missing skin mesh")
            skin.validate(meshes[skin.mesh_id],self.skeleton)
            instances=[n for n in self.scene.nodes if n.mesh_id==skin.mesh_id]
            require(bool(instances),"skin without scene instance")
            # Bind geometry in anchor-local coordinates. Reject ambiguous offset
            # instances rather than silently mixing spaces.
            require(all(all(abs(a-b)<1e-8 for a,b in zip(world[n.id].matrix,anchor.matrix))
                        for n in instances),"skin mesh instance must share anchor bind frame")
        ids={b.id for b in self.skeleton.bones}
        require(all(s.owner_id in (nodes if s.owner_kind=="node" else ids) for s in sockets),"unknown socket owner")
        object.__setattr__(self,"skins",tuple(sorted(skins,key=lambda s:s.mesh_id)))
        object.__setattr__(self,"sockets",tuple(sorted(sockets,key=lambda s:s.id)))

    def socket_world(self,id,pose=None):
        sockets={s.id:s for s in self.sockets}
        require(id in sockets,"unknown socket")
        s=sockets[id]
        world=self.scene.world_transforms()
        parent=world[s.owner_id] if s.owner_kind=="node" else world[self.anchor_node_id]@self.skeleton.transforms(pose)[s.owner_id]
        return parent@s.local

    def canonical_json(self):
        return json.dumps({"schema_version":1,"rig":asdict(self)},sort_keys=True,separators=(",",":"),allow_nan=False)

    def sha256(self):
        return hashlib.sha256(self.canonical_json().encode()).hexdigest()

def attachment_local(parent_world,target_socket_world,source_socket_local):
    """Local transform placing source socket exactly on target socket."""
    return inverse(parent_world)@target_socket_world@inverse(source_socket_local)
