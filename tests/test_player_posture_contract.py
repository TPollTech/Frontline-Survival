"""Static regression contracts for crouch, prone, collision and ADS.

Run with: python -m unittest discover -s tests -p 'test_*.py'
Engine/Windows gameplay tests remain necessary.
"""
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
PLAYER = (ROOT / "scripts" / "player.gd").read_text(encoding="utf-8")
RUNTIME = (ROOT / "tests" / "runtime_wave_qa.gd").read_text(encoding="utf-8")


class PlayerPostureContractTests(unittest.TestCase):
    @staticmethod
    def body(name):
        return PLAYER.split(f"func {name}(", 1)[1].split("\nfunc ", 1)[0]

    def test_stances_are_physical_and_keep_feet_anchored(self):
        body = self.body("_update_posture")
        self.assertIn("capsule_shape.height = maxf(0.72, current_body_height)", body)
        self.assertIn("collider_node.position.y = (current_body_height - 1.8) * 0.5", body)
        self.assertNotIn("scale.y =", body)

    def test_crouch_prone_and_last_stand_have_independent_heights(self):
        body = self.body("_update_posture")
        self.assertIn('0.75 if desired_state in ["downed", "prone"]', body)
        self.assertIn('1.18 if desired_state == "crouch" else 1.8', body)
        self.assertIn('var desired_state := "downed" if downed', body)

    def test_headroom_query_uses_physics_and_ignores_player(self):
        body = self.body("_can_expand_to_height")
        for marker in ["PhysicsShapeQueryParameters3D.new()",
                       "params.shape = probe", "params.exclude = [get_rid()]",
                       "params.collision_mask = 1",
                       "direct_space_state.intersect_shape(params, 1).is_empty()"]:
            self.assertIn(marker, body)

    def test_clearance_probe_uses_foot_anchored_transform(self):
        body = self.body("_can_expand_to_height")
        self.assertIn("(target_height - 1.8) * 0.5", body)

    def test_standup_rejected_without_clearance(self):
        body = self.body("_update_posture")
        self.assertIn("desired_height > current_body_height + 0.025", body)
        self.assertIn("not _can_expand_to_height(desired_height)", body)
        self.assertIn("desired_height = current_body_height", body)

    def test_recovery_under_roof_cannot_leave_stale_downed_posture(self):
        body = self.body("_update_posture")
        self.assertIn('desired_state = "prone" if posture == "downed" and not downed else posture', body)

    def test_camera_follows_body_without_exiting_capsule(self):
        body = self.body("_update_posture")
        self.assertIn("camera_stand_height + (current_body_height - 1.8) * 0.88", body)
        self.assertIn("collider_node.position.y + capsule_shape.height * 0.5 - 0.12", body)
        self.assertIn("camera.position.y = minf(lerpf(", body)

    def test_posture_keeps_ads_available_when_alive(self):
        physics = self.body("_physics_process")
        aim_line = next(line for line in physics.splitlines() if line.strip().startswith("aim = "))
        self.assertIn("Input.is_mouse_button_pressed(MOUSE_BUTTON_RIGHT)", aim_line)
        self.assertIn("not downed", aim_line)
        self.assertNotIn('posture == "stand"', aim_line)
        self.assertIn("camera.fov = lerpf(camera.fov, target_fov", physics)

    def test_crouch_is_hold_and_prone_is_toggle(self):
        physics = self.body("_physics_process")
        event = self.body("_input")
        self.assertIn("Input.is_key_pressed(KEY_C) or Input.is_key_pressed(KEY_CTRL)", physics)
        self.assertIn("if event.keycode == KEY_Z and not downed:", event)
        self.assertIn("prone_requested = not prone_requested", event)

    def test_no_sprint_or_jump_when_low(self):
        physics = self.body("_physics_process")
        sprint = next(line for line in physics.splitlines() if "var sprinting :=" in line)
        jump = next(line for line in physics.splitlines() if "if jump_just_pressed" in line)
        self.assertIn('posture == "stand"', sprint)
        self.assertIn('posture == "stand"', jump)
        self.assertIn("not downed", sprint)
        self.assertIn("not downed", jump)

    def test_prone_and_crouch_spread_reduction(self):
        shoot = self.body("shoot")
        self.assertIn('if posture == "crouch":', shoot)
        self.assertIn("spread *= 0.82", shoot)
        self.assertIn('elif posture == "prone":', shoot)
        self.assertIn("spread *= 0.65", shoot)
        self.assertIn("var origin := camera.global_position", shoot)

    def test_runtime_low_roof_rejects_stand_and_keeps_camera_inside(self):
        self.assertIn("test_roof_box.size = Vector3(3.0, 0.2, 3.0)", RUNTIME)
        for marker in [
            "physics roof should block expanding the capsule to standing height",
            "releasing crouch under a physical roof must not force standing",
            "camera must stay below the prone capsule top",
            "Last Stand recovery under a roof must not keep a stale downed posture",
            "player must stand again once the physical roof is removed",
        ]:
            self.assertIn(marker, RUNTIME)


if __name__ == "__main__":
    unittest.main()
