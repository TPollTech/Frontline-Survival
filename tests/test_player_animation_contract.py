"""Contracts for FPS hand animation and reload state coordination.

Run via: python -m unittest discover -s tests -p 'test_*.py'
Static contracts are not visual acceptance; Godot integration tests hand offsets.
"""
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
PLAYER = (ROOT / "scripts" / "player.gd").read_text(encoding="utf-8")
RUNTIME = (ROOT / "tests" / "runtime_wave_qa.gd").read_text(encoding="utf-8")


class FPSAnimationContractTests(unittest.TestCase):
    def body(self, name):
        return PLAYER.split(f"func {name}(", 1)[1].split("\nfunc ", 1)[0]

    def test_ads_drops_before_reload(self):
        physics = self.body("_physics_process")
        aim = next(line for line in physics.splitlines() if line.strip().startswith("aim = "))
        self.assertIn("not reloading", aim)
        self.assertIn("not controls_locked", aim)
        self.assertIn("not downed", aim)

    def test_support_hand_group_is_parented_to_viewmodel(self):
        build = self.body("_update_gun_mesh")
        self.assertIn('hand_rig.name = "Hands"', build)
        self.assertIn("viewmodel_root.add_child(hand_rig)", build)
        self.assertIn('left_hand_rig.name = "SupportArm"', build)
        self.assertIn("hand_rig.add_child(left_hand_rig)", build)

    def test_only_long_guns_render_support_arm(self):
        build = self.body("_update_gun_mesh")
        self.assertIn('var long_gun := weapon_id != "pistol"', build)
        self.assertIn("if long_gun:", build)
        self.assertIn("_add_first_person_arm(", build)

    def test_magazine_animation_has_closed_return_curve(self):
        animate = self.body("_animate_viewmodel")
        self.assertIn("smoothstep(0.12, 0.32, t)", animate)
        self.assertIn("1.0 - smoothstep(0.61, 0.84, t)", animate)
        self.assertIn("magazine_part.position = magazine_part.position.lerp(", animate)

    def test_magazine_fed_support_reaches_loading_hand(self):
        animate = self.body("_animate_viewmodel")
        self.assertIn('if weapon_id != "pistol" and reloading:', animate)
        self.assertIn("support_reload_offset = Vector3(0.10, -0.20, 0.24) * mag_out", animate)

    def test_shotgun_support_tracks_same_pump_as_action(self):
        animate = self.body("_animate_viewmodel")
        self.assertIn('if weapon_id == "shotgun":', animate)
        self.assertIn("support_reload_offset = Vector3(0.0, -0.045 * reload_tilt, pump)", animate)
        self.assertIn("viewmodel_depth + cycling + rack + pump", animate)

    def test_support_hand_preserves_sprint_and_grenade_motion(self):
        animate = self.body("_animate_viewmodel")
        self.assertIn("sprint_stride * 0.046", animate)
        self.assertIn("Vector3(-0.18, -0.41 + sprint_stride * 0.046, 0.25) * sprint_ease", animate)
        self.assertIn("sin(PI * clampf(grenade_throw_timer / 0.45, 0.0, 1.0))", animate)

    def test_support_hand_returns_to_neutral_when_timer_ends(self):
        animate = self.body("_animate_viewmodel")
        self.assertIn("var support_reload_offset := Vector3.ZERO", animate)
        self.assertIn("support_reload_offset,", animate)
        self.assertIn("left_hand_rig.position = left_hand_rig.position.lerp(", animate)

    def test_runtime_qa_covers_long_guns_shotgun_and_pistol(self):
        for marker in (
            'for gun_id: String in ["smg", "rifle", "lmg"]:',
            "support hand failed to reach magazine while reloading",
            "support hand did not return to the foregrip after",
            "shotgun support hand must track the pump during reload",
            "pistol must not render a floating support hand",
        ):
            self.assertIn(marker, RUNTIME)


if __name__ == "__main__":
    unittest.main()
