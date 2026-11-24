"""Source contracts for the user-facing FOV setting and its engine QA."""
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
def source(path):
    return (ROOT / path).read_text(encoding="utf-8")

class FovContracts(unittest.TestCase):
    def test_menu_and_persistence_use_shared_limits(self):
        menu = source("scripts/game_menu.gd")
        settings = source("scripts/game_settings.gd")
        self.assertIn('_slider("Campo de visão (FOV)", "fov", GameSettings.field_of_view, GameSettings.FOV_MIN, GameSettings.FOV_MAX, 1.0)', menu)
        for text in ('FOV_MIN := 60.0', 'FOV_DEFAULT := 76.0', 'FOV_MAX := 100.0',
                     'cfg.set_value("controls", "fov", field_of_view)',
                     '_normalize_fov(cfg.get_value("controls", "fov", FOV_DEFAULT))',
                     'clampf(degrees, FOV_MIN, FOV_MAX) if is_finite(degrees)'):
            self.assertIn(text, settings)
    def test_player_and_qa_share_camera_target(self):
        player = source("scripts/player.gd")
        qa = source("tests/fov_settings_qa.gd")
        workflow = source(".github/workflows/windows-build.yml")
        self.assertIn("GameSettings.changed.connect(_on_camera_settings_changed)", player)
        self.assertIn("camera.fov = get_target_camera_fov(false)", player)
        self.assertIn("get_target_camera_fov(sprint_blend * motion_ratio > 0.55)", player)
        for text in ("FOV slider missing from main menu", "pause slider did not update camera",
                     "config reload lost FOV", "ADS must override sprint", "Sentinela scope projection changed"):
            self.assertIn(text, qa)
        self.assertIn("--script res://tests/fov_settings_qa.gd", workflow)
        self.assertIn("QA_FOV_PASS", workflow)
