"""Hybrid arsenal contract (02-02): the eight production weapons keep the
silhouette envelope they had before the sculpted lofts were introduced.

The envelopes below are the measured AABBs of the pre-02-02 production GLBs.
They are the integration contract (viewmodel framing, wall clipping, scope
alignment), so a sculpted grip or stock may round the corners but must not
grow or shrink the weapon around them.
"""
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

import trimesh

import tools.build_weapons as build

ENVELOPES = {
    "pistol": (0.1188, 0.3875, 0.3930),
    "smg": (0.2800, 0.6415, 1.2785),
    "rifle": (0.1865, 0.6417, 1.7335),
    "shotgun": (0.2340, 0.4671, 1.9775),
    "lmg": (0.4299, 0.7800, 1.9855),
    "sniper": (0.3532, 0.6223, 2.3125),
    "bolt_sniper": (0.2905, 0.5185, 2.3860),
    "sentinela": (0.1672, 0.3800, 1.7875),
}
TOLERANCE_M = 0.002
TRIANGLE_CEILING = 18000
SCULPTED_PARTS = {
    "pistol": ("grip",),
    "smg": ("foregrip", "pistol_grip"),
    "rifle": ("wood_stock", "grip"),
    "shotgun": ("pump_action", "solid_stock", "vertical_grip", "pistol_grip"),
    "lmg": ("heavy_stock", "pistol_grip"),
    "sniper": ("precision_stock", "pistol_grip"),
    "bolt_sniper": ("stock_body", "cheek_rest", "grip_stock"),
    "sentinela": ("heavy_stock", "lower_handguard", "grip"),
}


def _build_all():
    """Re-run every recipe into a temporary directory and keep the scenes."""
    scenes = {}
    original = build.Gun.save

    def capture(self, name):
        scenes[name] = dict(self.scene.geometry)
        return original(self, name)

    with TemporaryDirectory() as out:
        build.OUT = Path(out)
        build.Gun.save = capture
        try:
            for key in build.RECIPES:
                build.RECIPES[key]()
        finally:
            build.Gun.save = original
    return scenes


class HybridArsenalContract(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.scenes = _build_all()

    def test_every_production_weapon_has_sculpted_furniture(self):
        for weapon, labels in SCULPTED_PARTS.items():
            present = {key.rsplit("_", 1)[0] for key in self.scenes[weapon]}
            for label in labels:
                self.assertIn(label, present, f"{weapon}: missing {label}")

    def test_sculpted_parts_are_closed_solids(self):
        for weapon, scene in self.scenes.items():
            for key, mesh in scene.items():
                self.assertTrue(mesh.is_watertight, f"{weapon}/{key} not watertight")
                self.assertTrue(mesh.is_winding_consistent, f"{weapon}/{key} winding")
                self.assertGreater(mesh.volume, 0.0, f"{weapon}/{key} inverted")

    def test_envelope_is_preserved_for_every_weapon(self):
        for weapon, expected in ENVELOPES.items():
            merged = trimesh.util.concatenate(list(self.scenes[weapon].values()))
            dims = merged.bounds[1] - merged.bounds[0]
            for axis, want, got in zip("XYZ", expected, dims):
                self.assertAlmostEqual(
                    float(got), want, delta=TOLERANCE_M,
                    msg=f"{weapon}: {axis} envelope drifted to {got:.4f} m (was {want:.4f})")

    def test_triangle_budget(self):
        for weapon, scene in self.scenes.items():
            triangles = sum(len(mesh.faces) for mesh in scene.values())
            self.assertLessEqual(triangles, TRIANGLE_CEILING, f"{weapon}: {triangles} triangles")


if __name__ == "__main__":
    unittest.main()
