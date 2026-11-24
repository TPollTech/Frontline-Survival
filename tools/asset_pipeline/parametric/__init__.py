"""Canonical parametric foundation; independent of the engine and GUI."""
from .model import MeshSpec, MaterialSpec, NodeSpec, SceneSpec, Transform
from .recipes import Box, Cylinder, PythonBackend, GeometryBackend
from .advanced import Extrusion, Revolution
from .organic import BezierCurve, BezierPatch, LoftSection, OrganicLoft, CustomTopology
from .blender_backend import BlenderBackend, BlenderError

__all__ = ["MeshSpec", "MaterialSpec", "NodeSpec", "SceneSpec", "Transform",
           "Box", "Cylinder", "Extrusion", "Revolution", "BezierCurve", "BezierPatch",
           "LoftSection", "OrganicLoft", "CustomTopology", "PythonBackend", "GeometryBackend", "BlenderBackend", "BlenderError"]
