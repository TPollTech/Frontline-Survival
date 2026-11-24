"""Projection math and integration contracts for independent weapon FOV."""
from pathlib import Path
import math
import unittest

ROOT = Path(__file__).resolve().parents[1]
def source(name):
    return (ROOT / name).read_text(encoding="utf-8")

class IndependentFOV(unittest.TestCase):
    def test_exact_screen_projection_and_depth(self):
        for multiplier in (1.0, 0.70, 0.48, 0.29, 1.045):
            for weapon in (60.0, 76.0, 100.0):
                for world in (60.0, 76.0, 100.0):
                    w = math.tan(math.radians(world * multiplier / 2))
                    v = math.tan(math.radians(weapon * multiplier / 2))
                    factor = w / v
                    for x, y, z in ((0.3, -0.4, -1), (-0.2, 0.15, -0.6)):
                        self.assertAlmostEqual(x * factor / (-z * w), x / (-z * v))
                        self.assertAlmostEqual(y * factor / (-z * w), y / (-z * v))

    def test_adapter_is_parent_of_entire_rig(self):
        player = source("scripts/player.gd")
        for text in ("camera.add_child(viewmodel_projection)",
                     "viewmodel_projection.add_child(gun)",
                     "viewmodel_projection.scale = Vector3(factor, factor, 1.0)",
                     "_update_viewmodel_projection(delta, sprint_blend * motion_ratio > 0.55, fov_speed)"):
            self.assertIn(text, player)

    def test_menu_and_saved_value_are_independent(self):
        settings = source("scripts/game_settings.gd")
        self.assertIn('cfg.set_value("controls", "weapon_fov", weapon_field_of_view)', settings)
        self.assertIn('_normalize_fov(cfg.get_value("controls", "weapon_fov", FOV_DEFAULT))', settings)
        self.assertIn('"weapon_fov": weapon_field_of_view = _normalize_fov(value)', settings)
        self.assertIn('_slider("FOV das armas", "weapon_fov"', source("scripts/game_menu.gd"))
        self.assertIn("QA_PROJECTION_PASS", source(".github/workflows/windows-build.yml"))
