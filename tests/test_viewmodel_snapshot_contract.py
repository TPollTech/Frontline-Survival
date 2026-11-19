"""Regression contracts for the first-person action pose contact sheet."""
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
SNAPSHOT = (ROOT / "tests" / "viewmodel_qa_snapshot.gd").read_text(encoding="utf-8")
LAYOUT = (ROOT / "docs" / "qa" / "viewmodel_layout.md").read_text(encoding="utf-8")


class ViewmodelSnapshotContracts(unittest.TestCase):
    def test_six_reference_poses_and_three_action_poses(self):
        self.assertIn('["pistol", "smg", "rifle", "shotgun", "lmg", "rifle", "rifle", "shotgun", "pistol", "sniper", "sniper", "sniper"]', SNAPSHOT)
        self.assertIn("var ads: bool = idx in [5, 9, 10, 11]", SNAPSHOT)
        self.assertIn("if idx == 6 or idx == 7:", SNAPSHOT)
        self.assertIn("if idx == 8:", SNAPSHOT)

    def test_reloads_use_instantiated_player_constants(self):
        self.assertIn("get_script().get_script_constant_map().get", SNAPSHOT)
        self.assertIn('float(specs[id]["reload"])', SNAPSHOT)
        self.assertNotIn("GameSettings", SNAPSHOT)
        self.assertIn("game.player.reload_elapsed = 0.0", SNAPSHOT)

    def test_composite_is_nine_cells_and_documented(self):
        self.assertIn("CELL_W * 3, CELL_H * 4", SNAPSHOT)
        self.assertIn("twelve poses:", SNAPSHOT)
        self.assertIn("1920 × 1440", LAYOUT)
        self.assertIn("Inferior esquerdo", LAYOUT)
        self.assertIn("Inferior central", LAYOUT)
        self.assertIn("Inferior direito", LAYOUT)


if __name__ == "__main__":
    unittest.main()
