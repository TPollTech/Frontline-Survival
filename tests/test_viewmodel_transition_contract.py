"""Stage 4 contracts: staged weapon switch, idle motion, FPS glove envelope.

These source-level checks run in Python; Godot integration verifies runtime states.
They do not replace visual acceptance by the player on Windows.
"""
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
PLAYER = (ROOT / "scripts" / "player.gd").read_text(encoding="utf-8")
RUNTIME = (ROOT / "tests" / "runtime_wave_qa.gd").read_text(encoding="utf-8")


class ViewmodelTransitionContracts(unittest.TestCase):
    def body(self, name):
        return PLAYER.split(f"func {name}(", 1)[1].split("\nfunc ", 1)[0]

    def test_manual_swap_keeps_old_gun_visible_until_timer_ends(self):
        switch = self.body("switch_weapon")
        self.assertIn('if not force:', switch)
        self.assertIn("pending_weapon_id = id", switch)
        self.assertIn("holster_timer = HOLSTER_DURATION", switch)
        self.assertLess(switch.index("if not force:"), switch.index("weapon_id = id"))

    def test_forced_equips_bypass_pending_holster(self):
        switch = self.body("switch_weapon")
        self.assertIn('if force and pending_weapon_id != "":', switch)
        self.assertIn('pending_weapon_id = ""', switch)
        self.assertIn("holster_timer = 0.0", switch)
        self.assertIn("switch_weapon(next_weapon, true)", self.body("_advance_weapon_switch"))

    def test_manual_holster_can_be_cancelled_by_selecting_current_weapon(self):
        switch = self.body("switch_weapon")
        self.assertIn('if pending_weapon_id != "" and id == weapon_id:', switch)
        self.assertIn("pending_weapon_id = id", switch)

    def test_pending_swap_aborts_when_dead_or_locked(self):
        advance = self.body("_advance_weapon_switch")
        self.assertIn("if dead or downed or controls_locked:", advance)
        self.assertIn("holster_timer = maxf(0.0, holster_timer - delta)", advance)
        self.assertIn("switch_weapon(next_weapon, true)", advance)

    def test_shoot_reload_and_melee_block_during_holster(self):
        for fn in ("shoot", "start_reload", "melee"):
            self.assertIn('pending_weapon_id != ""', self.body(fn))

    def test_ads_waits_for_holster_and_equip(self):
        physics = self.body("_physics_process")
        aim_line = next(s for s in physics.splitlines() if s.strip().startswith("aim = "))
        self.assertIn('pending_weapon_id == ""', aim_line)
        self.assertIn("equip_anim_timer <= 0.0", aim_line)

    def test_renews_equip_animation_after_holster(self):
        build = self.body("_update_gun_mesh")
        self.assertIn("equip_anim_timer = 0.34", build)
        self.assertIn("_update_gun_mesh()", self.body("switch_weapon"))

    def test_idle_breathing_and_walk_bob_are_separate(self):
        animate = self.body("_animate_viewmodel")
        self.assertIn("idle_breath:", animate)
        self.assertIn("sin(idle_clock * 1.6)", animate)
        self.assertIn("walk_bob:", animate)
        self.assertIn("sin(walk_clock) * 0.009 * walk_anim_blend", animate)
        self.assertIn("walk_anim_blend = motion_ratio * (1.0 - sprint_ease)", self.body("_physics_process"))

    def test_holster_blend_drives_visual_y_and_rotation(self):
        animate = self.body("_animate_viewmodel")
        self.assertIn("1.0 - holster_timer / HOLSTER_DURATION", animate)
        self.assertIn("- 0.40 * holster_blend", animate)
        self.assertIn("+ 0.30 * holster_blend", animate)

    def test_integration_covers_pending_fire_cancel_and_geometry(self):
        for line in (
            "outgoing gun should visibly lower while the old model remains mounted",
            "switching blocks fire/reload while waiting for the incoming model",
            "forced equip must cancel a queued manual weapon switch",
            "selecting the currently equipped gun should cancel a pending holster",
            "trigger glove is behind camera or outside FPS framing for",
            "support glove is behind camera or outside FPS framing for",
        ):
            self.assertIn(line, RUNTIME)


if __name__ == "__main__":
    unittest.main()
