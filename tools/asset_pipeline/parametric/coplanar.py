"""Conservative simplification of a validated CSG triangular solid.

Merge connected coplanar patches, not arbitrary nearby vertices. Only replace
the complete solid when every patch has one simple boundary and the candidate
passes independent topology, area, bounds and signed-volume checks.
"""
import math
from collections import defaultdict
from .model import MeshSpec, cross, sub, dot, require
from .advanced import triangulate_profile

def _norm(v):
    return math.sqrt(dot(v,v))

def _area(mesh):
    return sum(_norm(cross(sub(mesh.vertices[b],mesh.vertices[a]),
                           sub(mesh.vertices[c],mesh.vertices[a])))*0.5
               for a,b,c in mesh.triangles)

def simplify_coplanar_solid(mesh):
    if not mesh.closed_oriented() or mesh.signed_volume()<=0:
        raise ValueError("simplification requires closed outward solid")
    try:
        return _simplify(mesh)
    except ValueError:
        # Unsupported patches (holes, non-simple boundary, numerical issues)
        # keep the already validated original solid, never invent geometry.
        return mesh

def _simplify(mesh):
    vs,fs=mesh.vertices,mesh.triangles
    lo,hi=mesh.bounds()
    span=max(b-a for a,b in zip(lo,hi))
    tol=min(1e-7,max(1e-10,span*1e-8))
    normals=[]
    edges=defaultdict(list)
    for i,(a,b,c) in enumerate(fs):
        n=cross(sub(vs[b],vs[a]),sub(vs[c],vs[a]))
        mag=_norm(n)
        normals.append(tuple(x/mag for x in n))
        for u,v in ((a,b),(b,c),(c,a)):
            edges[min(u,v),max(u,v)].append((i,u,v))
    adjacent=defaultdict(list)
    for pair in edges.values():
        require(len(pair)==2,"nonmanifold edge")
        a,b=pair
        adjacent[a[0]].append(b[0])
        adjacent[b[0]].append(a[0])
    # Compare each prospective face to the fixed seed plane, not a chain
    # of tiny angles that could flatten an intentionally curved surface.
    groups=[]
    labels={}
    for seed in range(len(fs)):
        if seed in labels:
            continue
        gid=len(groups)
        n=normals[seed]
        origin=vs[fs[seed][0]]
        group=[]
        stack=[seed]
        labels[seed]=gid
        while stack:
            i=stack.pop()
            group.append(i)
            for j in adjacent[i]:
                if j in labels:
                    continue
                if dot(n,normals[j])<=0 or _norm(cross(n,normals[j]))>1e-6:
                    continue
                if any(abs(dot(n,sub(vs[k],origin)))>tol for k in fs[j]):
                    continue
                labels[j]=gid
                stack.append(j)
        groups.append(group)
    # Directed boundaries retain original face orientation. A patch with
    # holes/multiple loops is deliberately unsupported in this pass.
    outgoing=[{} for _ in groups]
    incoming=[set() for _ in groups]
    for pair in edges.values():
        (i,u,v),(j,w,x)=pair
        if labels[i]==labels[j]:
            continue
        for f,a,b in ((i,u,v),(j,w,x)):
            g=labels[f]
            require(a not in outgoing[g] and b not in incoming[g],"branched boundary")
            outgoing[g][a]=b
            incoming[g].add(b)
    loops=[]
    removable=defaultdict(list)
    for g,links in enumerate(outgoing):
        require(len(links)>=3 and set(links)==incoming[g],"invalid patch boundary")
        first=min(links)
        loop=[first]
        cur=links[first]
        while cur!=first:
            require(cur in links and cur not in loop,"invalid boundary loop")
            loop.append(cur)
            cur=links[cur]
        require(len(loop)==len(links),"patch has holes or multiple boundaries")
        loops.append(loop)
        for k,i in enumerate(loop):
            a,b,c=vs[loop[k-1]],vs[i],vs[loop[(k+1)%len(loop)]]
            line=sub(c,a)
            length=_norm(line)
            straight=length>tol and _norm(cross(sub(b,a),line))/length<=tol
            between=0<dot(sub(b,a),line)<length*length
            removable[i].append(straight and between)
    # Remove a boundary vertex only if every incident region agrees.
    # This preserves creases and prevents T-junctions.
    drop={i for i,flags in removable.items() if all(flags)}
    result=[]
    for gid,loop in enumerate(loops):
        loop=[i for i in loop if i not in drop]
        require(len(loop)>=3,"collapsed region")
        n=normals[groups[gid][0]]
        axis=max(range(3),key=lambda i:abs(n[i]))
        uv=[(vs[i][(axis+1)%3],vs[i][(axis+2)%3]) for i in loop]
        mapping=dict(zip(uv,loop))
        require(len(mapping)==len(loop),"duplicate projected vertex")
        polygon,faces=triangulate_profile(uv)
        for face in faces:
            a,b,c=(mapping[polygon[i]] for i in face)
            result.append((a,b,c) if n[axis]>0 else (a,c,b))
    used=sorted({i for f in result for i in f})
    if len(used)>=len(vs) and len(result)>=len(fs):
        return mesh
    remap={i:j for j,i in enumerate(used)}
    candidate=MeshSpec(mesh.id,[vs[i] for i in used],
                       [tuple(remap[i] for i in f) for f in result])
    require(candidate.closed_oriented() and candidate.signed_volume()>0,"invalid simplified topology")
    require(all(abs(a-b)<=tol for u,v in zip(mesh.bounds(),candidate.bounds()) for a,b in zip(u,v)),
            "simplification changed bounds")
    require(math.isclose(mesh.signed_volume(),candidate.signed_volume(),rel_tol=1e-7,
                         abs_tol=max(1e-15,4*tol*span*span)),"simplification changed volume")
    require(math.isclose(_area(mesh),_area(candidate),rel_tol=1e-7,
                         abs_tol=max(1e-15,4*tol*span)),"simplification changed surface area")
    return candidate
