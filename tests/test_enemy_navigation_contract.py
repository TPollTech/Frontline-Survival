"""Enemy obstacle recovery: maintain a flank, avoid premature cancellation."""
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
ENEMY = (ROOT / "scripts" / "enemy.gd").read_text(encoding="utf-8")
RUNTIME = (ROOT / "tests" / "runtime_wave_qa.gd").read_text(encoding="utf-8")


def body(name: str) -> str:
    return ENEMY.split(f"func {name}(", 1)[1].split("\nfunc ", 1)[0]


class EnemyNavigationContracts(unittest.TestCase):
    def test_wall_probes_preserve_committed_flank(self):
        nav = body("_update_obstacle_navigation")
        self.assertIn("detour_remaining <= 0.0 or detour_direction.length_squared() < 0.01", nav)
        self.assertIn("detour_remaining = maxf(detour_remaining, 0.85)", nav)
        self.assertNotIn("randf() < 0.40", nav)

    def test_close_enemy_behind_wall_can_detour(self):
        nav = body("_update_obstacle_navigation")
        self.assertIn("(distance <= goal_distance and visible)", nav)
        self.assertIn("ObstacleSteering.blocked(self, direction, 2.35)", nav)
        self.assertIn("_update_obstacle_navigation(delta, direction, distance, goal_distance, visible)", body("_physics_process"))

    def test_no_double_steering_and_reload_not_stall(self):
        physics = body("_physics_process")
        self.assertEqual(physics.count("detour_direction * 0.90"), 1)
        self.assertIn("chase and reload_remaining <= 0.0 and stagger_remaining <= 0.0", physics)

    def test_stuck_cover_route_resets_to_advance(self):
        recovery = body("_recover_from_stall")
        self.assertIn('if tactical_state in ["seek_cover", "peek"]:', recovery)
        self.assertIn('tactical_state = "advance"', recovery)
        self.assertIn('_set_tactical_posture("stand")', recovery)
        self.assertNotIn("queue_free", recovery)

    def test_crowd_separation_is_local_and_cheap(self):
        method = body("_update_crowd_avoidance")
        self.assertIn("crowd_check = randf_range(0.16, 0.24)", method)
        self.assertIn('get_nodes_in_group("enemies")', method)
        self.assertIn("other.dead or other.get_parent() != get_parent()", method)
        self.assertIn("away.y = 0.0", method)
        self.assertIn("crowd_avoidance = crowd_avoidance.limit_length(1.0)", method)

    def test_wall_navigation_takes_priority_over_crowd(self):
        physics = body("_physics_process")
        self.assertIn("_update_crowd_avoidance(delta)", physics)
        self.assertIn("if chase and crowd_avoidance.length_squared() > 0.002:", physics)
        self.assertIn("0.30 if detour_remaining > 0.0 else 0.65", physics)
        self.assertLess(physics.index("detour_direction * 0.90"), physics.index("crowd_avoidance * crowd_weight"))

    def test_six_enemy_corridor_regression_and_dead_filter(self):
        self.assertIn("for crowd_index in range(6):", RUNTIME)
        self.assertIn("outer soldiers in a crowded corridor must choose opposite separation", RUNTIME)
        self.assertIn("fallen squadmates must not keep pushing living enemies", RUNTIME)

    def test_live_wall_regression(self):
        for marker in (
            "physical wall must block the NPC's approach",
            "enemy behind nearby wall must select a viable flank",
            "repeated wall scans must not randomly reverse a committed flank",
            "stuck NPC must abandon blocked cover and resume movement",
        ):
            self.assertIn(marker, RUNTIME)


if __name__ == "__main__":
    unittest.main()
