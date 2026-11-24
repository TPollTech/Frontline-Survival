"""Canonical parametric foundation; independent of the engine and GUI."""
from .model import MeshSpec, MaterialSpec, NodeSpec, SceneSpec, Transform
from .recipes import Box, Cylinder, PythonBackend, GeometryBackend
from .advanced import Extrusion, Revolution
from .organic import BezierCurve, BezierPatch, LoftSection, OrganicLoft, CustomTopology
from .blender_backend import BlenderBackend, BlenderError
from .shading import RenderMesh, corner_normals, planar_uv, triangle_atlas_uv, corner_tangents, build_render_mesh
from .shading_blender import blender_tangents
from .pbr import TextureData, PBRMaterial, MaterialLibrary, generate_library
from .rig import BoneSpec, SkeletonSpec, SkinSpec, SocketSpec, RigSpec, inverse, rotation, around_pivot, reparent, attachment_local
from .lod import CategoryBudget, ColliderSpec, LODLevel, AssetLOD, resample_recipe, build_single_recipe_lods

from .exporter import source_manifest, export_bundle, write_bundle, verify_bundle

__all__ = ["MeshSpec", "MaterialSpec", "NodeSpec", "SceneSpec", "Transform",
           "Box", "Cylinder", "Extrusion", "Revolution", "BezierCurve", "BezierPatch",
           "LoftSection", "OrganicLoft", "CustomTopology", "PythonBackend", "GeometryBackend", "BlenderBackend", "BlenderError",
           "RenderMesh", "corner_normals", "planar_uv", "triangle_atlas_uv", "corner_tangents", "build_render_mesh", "blender_tangents",
           "TextureData", "PBRMaterial", "MaterialLibrary", "generate_library",
           "BoneSpec", "SkeletonSpec", "SkinSpec", "SocketSpec", "RigSpec", "inverse", "rotation", "around_pivot", "reparent", "attachment_local",
           "CategoryBudget", "ColliderSpec", "LODLevel", "AssetLOD", "resample_recipe", "build_single_recipe_lods", "source_manifest", "export_bundle", "write_bundle", "verify_bundle"]
