"""Stage 4 contract: physical gun-tucking near world obstacles."""
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
PLAYER = (ROOT / "scripts" / "player.gd").read_text(encoding="utf-8")
RUNTIME = (ROOT / "tests" / "runtime_wave_qa.gd").read_text(encoding="utf-8")


class WallClipProtectionContracts(unittest.TestCase):
    def body(self, name):
        return PLAYER.split(f"func {name}(", 1)[1].split("\nfunc ", 1)[0]

    def test_world_geometry_not_player_causes_tuck(self):
        sample = self.body("_weapon_wall_proximity")
        self.assertIn("PhysicsRayQueryParameters3D.create(origin, origin + direction * reach)", sample)
        self.assertIn("query.collision_mask = 1", sample)
        self.assertIn("query.exclude = [get_rid()]", sample)
        self.assertIn("direct_space_state.intersect_ray(query)", sample)

    def test_proximity_is_proportional_and_clamped(self):
        sample = self.body("_weapon_wall_proximity")
        self.assertIn("if hit.is_empty():", sample)
        self.assertIn("return 0.0", sample)
        self.assertIn("return clampf((reach - distance) / 0.70, 0.0, 1.0)", sample)

    def test_long_guns_have_more_clearance_than_pistol(self):
        self.assertIn('0.75 if weapon_id == "pistol" else 1.25', self.body("_weapon_wall_proximity"))

    def test_gun_tucks_and_rotates_without_moving_camera(self):
        physics = self.body("_physics_process")
        self.assertIn("weapon_wall_blend = move_toward(weapon_wall_blend, _weapon_wall_proximity(), delta * 7.0)", physics)
        self.assertIn("gun_target.z += 0.42 * weapon_wall_blend", physics)
        self.assertIn("gun_target.y -= 0.11 * weapon_wall_blend", physics)
        self.assertIn("- 0.26 * weapon_wall_blend", physics)

    def test_close_wall_prevents_ads_and_reticle(self):
        physics = self.body("_physics_process")
        aim = next(s for s in physics.splitlines() if s.strip().startswith("aim = "))
        self.assertIn("weapon_wall_blend < 0.30", aim)
        self.assertIn("optic_reticle.visible = aim and not reloading and weapon_wall_blend < 0.30", physics)

    def test_integration_uses_real_wall_and_frees_it(self):
        for marker in ("var wall_probe := StaticBody3D.new()",
                       "wall_probe.global_transform = Transform3D(",
                       "nearby wall must tuck the long gun before muzzle clipping",
                       "pistol should need less wall clearance than the long gun",
                       "wall tuck must release when a physical obstruction is removed",
                       "wall_probe.queue_free()"):
            self.assertIn(marker, RUNTIME)


if __name__ == "__main__":
    unittest.main()
