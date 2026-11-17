"""Protect the wave loop from stale logical enemy counts."""
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
MAIN = (ROOT / "scripts" / "main.gd").read_text(encoding="utf-8")
RUNTIME = (ROOT / "tests" / "runtime_wave_qa.gd").read_text(encoding="utf-8")


def function_body(name: str) -> str:
    return MAIN.split(f"func {name}(", 1)[1].split("\nfunc ", 1)[0]


class WaveCounterReconciliationContracts(unittest.TestCase):
    def test_reconciliation_counts_only_real_live_enemies_of_game(self):
        body = function_body("_reconcile_active_enemies")
        self.assertIn('get_nodes_in_group("enemies")', body)
        self.assertIn("enemy.get_parent() == self and not enemy.dead", body)
        self.assertIn("alive = actual_alive", body)
        self.assertNotIn("wallet +=", body)
        self.assertNotIn("kills +=", body)

    def test_wave_loop_checks_count_before_ending(self):
        physics = function_body("_physics_process")
        self.assertIn("wave_reconcile_timer -= delta", physics)
        self.assertIn("(spawn_remaining <= 0 and alive <= 0)", physics)
        self.assertLess(physics.index("_reconcile_active_enemies()"), physics.index("_end_wave()"))
        self.assertIn("wave_reconcile_timer = 0.75", physics)
        self.assertIn("wave_reconcile_timer = 0.0", function_body("_begin_wave"))

    def test_regression_exercises_premature_finish_and_ghost_count(self):
        for s in ("a zero counter must not finish the wave while a living enemy exists",
                  "counter recovery must remove phantom active enemies",
                  "freed enemy left a phantom alive count",
                  "scene reconciliation must not award credits or kills"):
            self.assertIn(s, RUNTIME)


if __name__ == "__main__":
    unittest.main()
