"""Deterministic triangle contact audit in source bind or posed coordinates.

Broad phase: spatial cells with AABB filtering. Narrow phase: triangle
separating axes, including coplanar in-plane axes. Shared-index pairs are
excluded; contacts within tolerance count. This is not a proof of absence
of overlap at adjacent faces or of continuous collision during animation.
"""
import itertools
import math
from .model import dot,cross,sub

def intersects(a,b,eps=1e-8):
    e=[sub(a[(i+1)%3],a[i]) for i in range(3)]
    f=[sub(b[(i+1)%3],b[i]) for i in range(3)]
    n=cross(e[0],e[1]);m=cross(f[0],f[1])
    axes=[n,m]+[cross(u,v) for u in e for v in f]
    axes.extend(cross(n,u) for u in e+f)
    axes.extend(cross(m,u) for u in e+f)
    for axis in axes:
        length=math.sqrt(dot(axis,axis))
        if length<1e-18:continue
        p=[dot(x,axis) for x in a];q=[dot(x,axis) for x in b]
        tol=eps*length
        if max(p)<min(q)-tol or max(q)<min(p)-tol:return False
    return True

def audit(vertices,triangles,eps=1e-8):
    vs=tuple(vertices);fs=tuple(triangles)
    extent=max(max(v[i] for v in vs)-min(v[i] for v in vs) for i in range(3))
    cell=max(extent/24,eps*100)
    cells={};bounds=[];points=[];ids=[];pairs=0;examples=[];tested=0
    for i,face in enumerate(fs):
        tri=tuple(vs[j] for j in face);points.append(tri);ids.append(set(face))
        lo=tuple(min(v[k] for v in tri) for k in range(3));hi=tuple(max(v[k] for v in tri) for k in range(3))
        bounds.append((lo,hi))
        keys=list(itertools.product(*(range(math.floor((a-eps)/cell),math.floor((b+eps)/cell)+1) for a,b in zip(lo,hi))))
        candidates=set(j for k in keys for j in cells.get(k,()))
        for j in sorted(candidates):
            if ids[i]&ids[j]:continue
            p,q=bounds[j]
            if any(a>d+eps or c>b+eps for a,b,c,d in zip(lo,hi,p,q)):continue
            tested+=1
            if intersects(tri,points[j],eps):
                pairs+=1
                if len(examples)<12:examples.append([j,i])
        for key in keys:cells.setdefault(key,[]).append(i)
    return {"contact_pairs":pairs,"tested_pairs":tested,"examples":examples,"tolerance_m":eps,"scope":"nonadjacent_triangle_contacts","excluded":"shared_index_pairs"}
