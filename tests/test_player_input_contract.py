"""Static regression checks; run: python -m unittest discover -s tests."""
from pathlib import Path
import unittest

PLAYER = Path(__file__).resolve().parents[1] / "scripts" / "player.gd"

class PlayerInputContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = PLAYER.read_text(encoding="utf-8")

    def test_jump_requires_fresh_press(self):
        self.assertIn("var jump_was_held: bool = false", self.source)
        self.assertIn("var jump_held: bool = Input.is_key_pressed(KEY_SPACE)", self.source)
        self.assertIn("var jump_just_pressed: bool = jump_held and not jump_was_held", self.source)
        self.assertIn("jump_was_held = jump_held", self.source)
        self.assertIn('if jump_just_pressed and is_on_floor() and posture == "stand" and not downed and not controls_locked:', self.source)
        self.assertNotIn("Input.is_key_just_pressed(", self.source)

    def test_sprint_requires_ground_contact(self):
        physics = self.source.split("func _physics_process(delta: float) -> void:", 1)[1]
        sprint_line = next(line.strip() for line in physics.splitlines() if line.strip().startswith("var sprinting :="))
        self.assertIn("Input.is_key_pressed(KEY_SHIFT)", sprint_line)
        self.assertIn("is_on_floor()", sprint_line)
        self.assertIn('posture == "stand"', sprint_line)
        self.assertIn("not controls_locked", sprint_line)

    def test_camera_ads_requires_captured_mouse(self):
        physics = self.source.split("func _physics_process(delta: float) -> void:", 1)[1]
        aim_line = next(line.strip() for line in physics.splitlines() if line.strip().startswith("aim = "))
        self.assertIn("Input.get_mouse_mode() == Input.MOUSE_MODE_CAPTURED", aim_line)
        self.assertIn("not controls_locked", aim_line)

    def test_footstep_animation_uses_actual_ground_velocity(self):
        physics = self.source.split("func _physics_process(delta: float) -> void:", 1)[1]
        self.assertIn("Vector2(velocity.x, velocity.z).length() if is_on_floor() else 0.0", physics)
        self.assertIn("ground_motion / maxf(speed, 0.1)", physics)
        self.assertIn("walk_clock += delta * motion_ratio", physics)
        self.assertIn("sprint_stride = sin(walk_clock * 1.16) * sprint_blend * motion_ratio", physics)
        self.assertNotIn("walk_clock += delta * movement.length()", physics)

    def test_sprint_weapon_animation_requires_actual_movement(self):
        physics = self.source.split("func _physics_process(delta: float) -> void:", 1)[1]
        physics = physics.split("\nfunc _input(", 1)[0]
        self.assertIn(
            "var sprint_ease: float = sprint_blend * sprint_blend * (3.0 - 2.0 * sprint_blend) * motion_ratio",
            physics,
        )

    def test_sprint_fov_requires_actual_ground_movement(self):
        physics = self.source.split("func _physics_process(delta: float) -> void:", 1)[1]
        physics = physics.split("\nfunc _input(", 1)[0]
        self.assertIn("var motion_ratio: float = clampf(ground_motion / maxf(speed, 0.1), 0.0, 1.0)", physics)
        self.assertIn("sprint_blend * motion_ratio > 0.55", physics)
        self.assertLess(physics.index("var motion_ratio:"), physics.index("var target_fov:"))

    def test_mouse_look_requires_capture_and_clamps_pitch(self):
        events = self.source.split("func _input(event: InputEvent) -> void:", 1)[1]
        events = events.split("\nfunc shoot() -> void:", 1)[0]
        self.assertIn(
            "Input.get_mouse_mode() == Input.MOUSE_MODE_CAPTURED and not controls_locked and not dead:",
            events,
        )
        self.assertIn("rotate_y(-event.relative.x * 0.002 * GameSettings.mouse_sensitivity)", events)
        self.assertIn("camera.rotation.x = clampf(camera.rotation.x, -1.45, 1.45)", events)

    def test_weapon_scroll_requires_captured_mouse(self):
        events = self.source.split("func _input(event: InputEvent) -> void:", 1)[1]
        events = events.split("func shoot() -> void:", 1)[0]
        self.assertIn(
            "not controls_locked and Input.get_mouse_mode() == Input.MOUSE_MODE_CAPTURED:",
            events,
        )

    def test_shoot_checks_mouse_capture(self):
        shoot = self.source.split("func shoot() -> void:", 1)[1]
        shoot = shoot.split("\nfunc ", 1)[0]
        self.assertIn("suppress_fire_until_release", shoot)
        self.assertIn("Input.get_mouse_mode() != Input.MOUSE_MODE_CAPTURED", shoot)

    def test_recovery_click_suppresses_automatic_fire(self):
        self.assertIn("suppress_fire_until_release = true", self.source)
        self.assertIn("if suppress_fire_until_release and not Input.is_mouse_button_pressed(MOUSE_BUTTON_LEFT):", self.source)
        self.assertIn("if event is InputEventMouseButton and not event.pressed and event.button_index == MOUSE_BUTTON_LEFT:", self.source)

    def test_viewmodel_sprint_respects_actual_ground_movement(self):
        physics = self.source.split("func _physics_process(delta: float) -> void:", 1)[1]
        physics = physics.split("\nfunc _input(", 1)[0]
        self.assertIn("var sprint_ease: float = sprint_blend * sprint_blend * (3.0 - 2.0 * sprint_blend) * motion_ratio", physics)
        self.assertIn("_animate_viewmodel(delta, sprint_ease)", physics)
        viewmodel = self.source.split("func _animate_viewmodel(delta: float, sprint_ease: float) -> void:", 1)[1]
        viewmodel = viewmodel.split("\nfunc ", 1)[0]
        self.assertNotIn("var sprint_ease:", viewmodel)
        self.assertIn("sprint_stride * 0.046", viewmodel)

    def test_ads_does_not_activate_when_sprint_starts(self):
        physics = self.source.split("func _physics_process(delta: float) -> void:", 1)[1]
        sprint_pos = physics.index("var sprinting :=")
        aim_pos = physics.index("    aim = ")
        self.assertLess(sprint_pos, aim_pos)
        aim_line = next(line.strip() for line in physics.splitlines() if line.strip().startswith("aim = "))
        self.assertIn("not sprinting", aim_line)

if __name__ == "__main__":
    unittest.main()
