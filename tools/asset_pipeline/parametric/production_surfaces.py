"""Candidate multi-surface GLB exporter. No production integration yet.

Receives explicitly classified, world-space triangle meshes; never infers
material from colour or node name. Preserves authored vertex colours.
"""
import numpy as np
import trimesh


def export_profiled_surface(parts, profiles):
    """Export one identity mesh node with one primitive per used profile.

    parts: iterable of (profile_id, trimesh.Trimesh).
    profiles: mapping of ID to linear metallic/roughness factors.
    No texture authoring or filesystem writes are performed here.
    """
    groups = {}
    for profile, mesh in parts:
        if profile not in profiles:
            raise ValueError(f"unknown surface profile: {profile}")
        if not isinstance(mesh, trimesh.Trimesh) or not len(mesh.faces):
            raise ValueError("expected a nonempty triangle mesh")
        groups.setdefault(profile, []).append(mesh.copy())
    if not 1 <= len(groups) <= 8:
        raise ValueError("expected one to eight used profiles")
    scene = trimesh.Scene()
    materials = []
    for profile, meshes in sorted(groups.items()):
        factors = profiles[profile]
        metallic, roughness = (float(factors[k]) for k in ("metallic", "roughness"))
        if not (0 <= metallic <= 1 and 0 <= roughness <= 1):
            raise ValueError(f"invalid factors: {profile}")
        merged = trimesh.util.concatenate(meshes)
        if merged.visual.kind not in ("face", "vertex"):
            raise ValueError("expected authored colours")
        normals = merged.vertex_normals
        if not np.isfinite(normals).all() or not np.allclose(np.linalg.norm(normals, axis=1), 1):
            raise ValueError("invalid vertex normals")
        axes = np.eye(3)[np.argmin(np.abs(normals), axis=1)]
        tangents = np.cross(axes, normals)
        tangents /= np.linalg.norm(tangents, axis=1)[:, None]
        merged.vertex_attributes["_TANGENT"] = np.column_stack(
            (tangents, np.ones(len(normals)))
        ).astype(np.float32)
        scene.add_geometry(merged, geom_name=profile, node_name=profile)
        materials.append({"name": profile, "alphaMode": "OPAQUE", "doubleSided": False,
                          "pbrMetallicRoughness": {"baseColorFactor": [1, 1, 1, 1],
                                                   "metallicFactor": metallic,
                                                   "roughnessFactor": roughness}})

    def attach_materials(tree):
        # All input meshes are already in a shared world-space frame.
        slots = {m["name"]: i for i, m in enumerate(materials)}
        primitives = []
        for mesh in tree["meshes"]:
            if len(mesh["primitives"]) != 1:
                raise ValueError("unexpected exporter primitive layout")
            primitive = mesh["primitives"][0]
            attrs = primitive["attributes"]
            if not {"POSITION", "NORMAL", "COLOR_0", "_TANGENT"} <= attrs.keys():
                raise ValueError("missing authored surface attributes")
            attrs["TANGENT"] = attrs.pop("_TANGENT")
            primitive["material"] = slots[mesh["name"]]
            primitives.append(primitive)
        if sorted(p["material"] for p in primitives) != list(range(len(materials))):
            raise ValueError("surface coverage mismatch")
        tree["materials"] = materials
        tree["meshes"] = [{"name": "profiled_surface", "primitives": sorted(
            primitives, key=lambda p: p["material"])}]
        tree["nodes"] = [{"name": "profiled_surface", "mesh": 0}]
        tree["scenes"] = [{"nodes": [0]}]
        tree["scene"] = 0

    return scene.export(file_type="glb", include_normals=True,
                        tree_postprocessor=attach_materials)
