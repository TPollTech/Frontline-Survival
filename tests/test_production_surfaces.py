"""Focused synthetic tests for the isolated exporter, not a Godot test."""
import io
import json
import struct
import unittest
import numpy as np
import trimesh
from tools.asset_pipeline.parametric.production_surfaces import export_profiled_surface

PROFILES = {"metal": {"metallic": 1, "roughness": .42},
            "wood": {"metallic": 0, "roughness": .66}}


def fixture():
    parts = []
    for profile, offset, color in [("metal", 0, [50, 60, 70, 255]),
                                   ("wood", 2, [130, 70, 30, 255]),
                                   ("metal", 4, [80, 90, 100, 255])]:
        mesh = trimesh.creation.box()
        mesh.apply_translation([offset, 0, 0])
        mesh.visual.face_colors = color
        parts.append((profile, mesh))
    return parts


def document(data):
    length = struct.unpack_from("<I", data, 12)[0]
    return json.loads(data[20:20 + length])


class ProductionSurfaceTests(unittest.TestCase):
    def setUp(self):
        self.parts = fixture()
        self.data = export_profiled_surface(self.parts, PROFILES)
        self.doc = document(self.data)

    def test_deterministic(self):
        self.assertEqual(self.data, export_profiled_surface(self.parts, PROFILES))

    def test_explicit_surface_slots(self):
        self.assertEqual(len(self.doc["meshes"]), 1)
        self.assertEqual(len(self.doc["nodes"]), 1)
        self.assertEqual([p["material"] for p in self.doc["meshes"][0]["primitives"]], [0, 1])
        for mat in self.doc["materials"]:
            self.assertEqual(mat["alphaMode"], "OPAQUE")
            self.assertEqual(mat["pbrMetallicRoughness"]["metallicFactor"], PROFILES[mat["name"]]["metallic"])
            self.assertEqual(mat["pbrMetallicRoughness"]["roughnessFactor"], PROFILES[mat["name"]]["roughness"])

    def test_attributes_and_triangle_count(self):
        total = 0
        for p in self.doc["meshes"][0]["primitives"]:
            self.assertTrue({"POSITION", "COLOR_0", "NORMAL", "TANGENT"} <= p["attributes"].keys())
            total += self.doc["accessors"][p["indices"]]["count"] // 3
        self.assertEqual(total, sum(len(m.faces) for _, m in self.parts))

    def test_colors_and_tangent_frames(self):
        length = struct.unpack_from("<I", self.data, 12)[0]
        start = 20 + length + 8
        def read(index, dtype, width):
            acc = self.doc["accessors"][index]
            view = self.doc["bufferViews"][acc["bufferView"]]
            offset = start + view.get("byteOffset", 0) + acc.get("byteOffset", 0)
            return np.frombuffer(self.data, dtype=dtype, count=acc["count"] * width,
                                 offset=offset).reshape(-1, width)
        for p in self.doc["meshes"][0]["primitives"]:
            attrs = p["attributes"]
            profile = self.doc["materials"][p["material"]]["name"]
            colors = read(attrs["COLOR_0"], "u1", 4)
            expected = {tuple(m.visual.face_colors[0]) for k, m in self.parts if k == profile}
            self.assertEqual(set(map(tuple, colors)), expected)
            normals = read(attrs["NORMAL"], "<f4", 3)
            tangents = read(attrs["TANGENT"], "<f4", 4)
            np.testing.assert_allclose(np.linalg.norm(normals, axis=1), 1, atol=1e-6)
            np.testing.assert_allclose(np.linalg.norm(tangents[:, :3], axis=1), 1, atol=1e-6)
            np.testing.assert_allclose(np.sum(normals * tangents[:, :3], axis=1), 0, atol=1e-6)
            np.testing.assert_array_equal(tangents[:, 3], 1)

    def test_import_bounds(self):
        scene = trimesh.load(io.BytesIO(self.data), file_type="glb", force="scene", process=False)
        expected = trimesh.util.concatenate([m for _, m in self.parts])
        np.testing.assert_allclose(scene.bounds, expected.bounds)
        self.assertEqual(sum(len(m.faces) for m in scene.geometry.values()), len(expected.faces))

    def test_unknown_profile(self):
        with self.assertRaises(ValueError):
            export_profiled_surface([("missing", self.parts[0][1])], PROFILES)

    def test_invalid_factors(self):
        for value in (-1, 2, float("nan")):
            with self.assertRaises(ValueError):
                export_profiled_surface([self.parts[0]], {"metal": {"metallic": value, "roughness": .5}})

    def test_empty(self):
        with self.assertRaises(ValueError):
            export_profiled_surface([], PROFILES)

    def test_eight_slot_limit(self):
        profiles = {str(i): PROFILES["metal"] for i in range(9)}
        with self.assertRaises(ValueError):
            export_profiled_surface([(k, self.parts[0][1]) for k in profiles], profiles)


if __name__ == "__main__":
    unittest.main()
