"""Canonical parametric foundation; independent of the engine and GUI."""
from .model import MeshSpec, MaterialSpec, NodeSpec, SceneSpec, Transform
from .recipes import Box, Cylinder, PythonBackend, GeometryBackend
from .advanced import Extrusion, Revolution
from .blender_backend import BlenderBackend, BlenderError

__all__ = ["MeshSpec", "MaterialSpec", "NodeSpec", "SceneSpec", "Transform",
           "Box", "Cylinder", "Extrusion", "Revolution", "PythonBackend", "GeometryBackend", "BlenderBackend", "BlenderError"]
