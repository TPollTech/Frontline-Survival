"""Typed parametric recipes and backend protocol. More operations follow separately."""
from dataclasses import dataclass
from typing import Protocol
import math
from .model import MeshSpec, number, vector, require, stable_id
from .advanced import Extrusion, Revolution, build_advanced

@dataclass(frozen=True)
class Box:
    id: str
    size_m: tuple

    def __post_init__(self):
        stable_id(self.id)
        dims=vector(self.size_m,3)
        require(min(dims)>0,"box dimensions must be positive")
        object.__setattr__(self,"size_m",dims)

@dataclass(frozen=True)
class Cylinder:
    id: str
    radius_m: float
    height_m: float
    segments: int = 32

    def __post_init__(self):
        stable_id(self.id)
        radius,height=number(self.radius_m),number(self.height_m)
        require(radius>0 and height>0,"cylinder dimensions must be positive")
        require(type(self.segments) is int and 3<=self.segments<=512,"segments out of range")
        object.__setattr__(self,"radius_m",radius)
        object.__setattr__(self,"height_m",height)

class GeometryBackend(Protocol):
    def build(self, recipe: Box | Cylinder | Extrusion | Revolution) -> MeshSpec: ...

class PythonBackend:
    """Direct indexed meshes with outward CCW winding in canonical Y-up coordinates."""
    def build(self, recipe):
        if isinstance(recipe,Box):
            x,y,z=(v/2 for v in recipe.size_m)
            vertices=((-x,-y,-z),(x,-y,-z),(x,y,-z),(-x,y,-z),
                      (-x,-y,z),(x,-y,z),(x,y,z),(-x,y,z))
            triangles=((0,2,1),(0,3,2),(4,5,6),(4,6,7),(0,1,5),(0,5,4),
                       (3,7,6),(3,6,2),(0,4,7),(0,7,3),(1,2,6),(1,6,5))
        elif isinstance(recipe,Cylinder):
            n=recipe.segments
            r,h=recipe.radius_m,recipe.height_m/2
            vertices=[(r*math.cos(math.tau*i/n),y,r*math.sin(math.tau*i/n)) for y in (-h,h) for i in range(n)]
            vertices.extend(((0,-h,0),(0,h,0)))
            triangles=[]
            for i in range(n):
                j=(i+1)%n
                triangles.extend(((i,i+n,j+n),(i,j+n,j),(2*n,i,j),(2*n+1,j+n,i+n)))
        elif isinstance(recipe,(Extrusion,Revolution)):
            return build_advanced(recipe)
        else:
            raise TypeError("unsupported recipe")
        mesh=MeshSpec(recipe.id,vertices,triangles)
        require(mesh.closed_oriented() and mesh.signed_volume()>0,"invalid primitive winding")
        return mesh
