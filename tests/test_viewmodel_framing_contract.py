"""Framing policy and engine QA wiring regression checks."""
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[1]
PLAYER = (ROOT / "scripts/player.gd").read_text(encoding="utf-8")
QA = (ROOT / "tests/viewmodel_framing_qa.gd").read_text(encoding="utf-8")
SNAPSHOT = (ROOT / "tests/viewmodel_qa_snapshot.gd").read_text(encoding="utf-8")
WORKFLOW = (ROOT / ".github/workflows/windows-build.yml").read_text(encoding="utf-8")

class FramingContracts(unittest.TestCase):
    def test_all_weapons_have_mesh_profiles(self):
        profiles = PLAYER.split("const VIEWMODEL_PROFILES := {", 1)[1].split("}", 1)[0]
        self.assertEqual(set(re.findall(r'"(\w+)": Vector2', profiles)),
            {"pistol", "smg", "rifle", "shotgun", "lmg", "sentinela", "sniper", "bolt_sniper"})

    def test_mesh_bounds_and_shared_rest_pose(self):
        for fragment in ("local_transform * mesh_node.get_aabb()",
                         "viewmodel_rear_extent + camera.near + MODEL_NEAR_MARGIN",
                         "get_viewmodel_rest_pose(aim)", "HIP_REFERENCE_SLOPE.x * distance",
                         "return Vector3(0.0, -viewmodel_scale * get_sight_height(), ads_depth())"):
            self.assertIn(fragment, PLAYER)
        self.assertIn("get_viewmodel_rest_pose(ads)", SNAPSHOT)
        self.assertIn("get_viewmodel_rest_pose(ads)", QA)

    def test_rendered_qa_checks_geometry_not_only_screenshots(self):
        for fragment in ("neutral rear crosses near margin", "ADS sight axis not centered",
                         "hip horizontal framing drift", "hip vertical framing drift",
                         "QA_FRAMING_PASS"):
            self.assertIn(fragment, QA)
        self.assertIn("res://tests/viewmodel_framing_qa.gd", WORKFLOW)
        self.assertIn("docs/qa/weapon_framing.png", WORKFLOW)
