"""Static regression checks; run: python -m unittest discover -s tests."""
from pathlib import Path
import unittest

PLAYER = Path(__file__).resolve().parents[1] / "scripts" / "player.gd"

class PlayerInputContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = PLAYER.read_text(encoding="utf-8")

    def test_jump_requires_fresh_press(self):
        self.assertIn("Input.is_key_just_pressed(KEY_SPACE) and is_on_floor()", self.source)
        self.assertNotIn("Input.is_key_pressed(KEY_SPACE)", self.source)

    def test_shoot_checks_mouse_capture(self):
        shoot = self.source.split("func shoot() -> void:", 1)[1]
        shoot = shoot.split("\nfunc ", 1)[0]
        self.assertIn("suppress_fire_until_release", shoot)
        self.assertIn("Input.get_mouse_mode() != Input.MOUSE_MODE_CAPTURED", shoot)

    def test_recovery_click_suppresses_automatic_fire(self):
        self.assertIn("suppress_fire_until_release = true", self.source)
        self.assertIn("if suppress_fire_until_release and not Input.is_mouse_button_pressed(MOUSE_BUTTON_LEFT):", self.source)
        self.assertIn("if event is InputEventMouseButton and not event.pressed and event.button_index == MOUSE_BUTTON_LEFT:", self.source)

if __name__ == "__main__":
    unittest.main()
