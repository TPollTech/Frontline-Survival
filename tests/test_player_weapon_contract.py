"""Static contracts for player shooting, reloading and weapon swapping.

Run with: python -m unittest discover -s tests
These tests do not replace in-engine gameplay validation.
"""
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
PLAYER = ROOT / "scripts" / "player.gd"
INTEGRATION = ROOT / "tests" / "runtime_wave_qa.gd"
MAIN = ROOT / "scripts" / "main.gd"


class PlayerWeaponContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = PLAYER.read_text(encoding="utf-8")
        cls.runtime = INTEGRATION.read_text(encoding="utf-8")
        cls.main = MAIN.read_text(encoding="utf-8")

    def body(self, name):
        return self.source.split(f"func {name}(", 1)[1].split("\nfunc ", 1)[0]

    def test_five_distinct_weapon_classes(self):
        for weapon in ["pistol", "smg", "rifle", "shotgun", "lmg"]:
            self.assertIn(f'"{weapon}": {{', self.source)

    def test_fire_is_guarded_by_focus_and_lifecycle(self):
        shoot = self.body("shoot")
        for condition in ["dead", "controls_locked", "reloading",
                          "suppress_fire_until_release", "Input.MOUSE_MODE_CAPTURED"]:
            self.assertIn(condition, shoot)

    def test_fire_blocks_melee_grenade_and_equip(self):
        shoot = self.body("shoot")
        for condition in ["grenade_throw_timer > 0.0", "melee_timer > 0.0",
                          "equip_anim_timer > 0.0", "fire_timer > 0.0"]:
            self.assertIn(condition, shoot)

    def test_clip_is_checked_before_round_consumption(self):
        shoot = self.body("shoot")
        self.assertLess(shoot.index("if magazines[weapon_id] <= 0:"),
                        shoot.index("magazines[weapon_id] -= 1"))
        self.assertIn("start_reload()", shoot)

    def test_cooldown_uses_own_weapon_rate(self):
        shoot = self.body("shoot")
        self.assertIn('fire_timer = WEAPONS[weapon_id]["rate"]', shoot)

    def test_reload_rejects_invalid_states(self):
        reload = self.body("start_reload")
        for condition in ["dead", "controls_locked", "reloading", "downed",
                          "melee_timer > 0.0", "grenade_throw_timer > 0.0"]:
            self.assertIn(condition, reload)

    def test_reload_checks_capacity_and_reserve(self):
        reload = self.body("start_reload")
        self.assertIn('magazines[weapon_id] >= WEAPONS[weapon_id]["mag"]', reload)
        self.assertIn("reserves[weapon_id] <= 0", reload)

    def test_cancelled_reload_cannot_finish(self):
        finish = self.body("_finish_reload")
        self.assertIn("if not reloading:", finish)
        self.assertLess(finish.index("if not reloading:"), finish.index("magazines[weapon_id] += loaded"))

    def test_partial_reload_is_clamped_to_reserve(self):
        finish = self.body("_finish_reload")
        self.assertIn("var loaded: int = mini(needed, reserves[weapon_id])", finish)
        self.assertIn("magazines[weapon_id] += loaded", finish)
        self.assertIn("reserves[weapon_id] -= loaded", finish)

    def test_swap_cancels_reload_and_keeps_cooldown(self):
        swap = self.body("switch_weapon")
        self.assertIn("reloading = false", swap)
        self.assertIn("reload_timer = 0.0", swap)
        self.assertIn("reload_sound.stop()", swap)
        self.assertIn("fire_timer = maxf(fire_timer, 0.14)", swap)
        self.assertNotIn("fire_timer = 0.14", swap)

    def test_last_stand_only_equips_pistol(self):
        swap = self.body("switch_weapon")
        self.assertIn('(downed and id != "pistol")', swap)
        self.assertIn("not owned_weapons.has(id)", swap)

    def test_last_primary_tracks_successful_equips_and_swaps(self):
        equip = self.body("equip")
        swap = self.body("switch_weapon")
        self.assertNotIn("last_primary = id", equip)
        self.assertIn('if id != "pistol":\n        last_primary = id', swap)
        self.assertLess(swap.index("not owned_weapons.has(id)"),
                        swap.index("last_primary = id"))
        self.assertIn("switching to an owned primary must update the quick-toggle primary", self.runtime)
        self.assertIn("downed pickup must not overwrite the remembered active primary", self.runtime)

    def test_refill_resets_reload_visual_and_timer(self):
        refill = self.body("refill_ammo")
        for marker in ["reloading = false", "reload_timer = 0.0",
                       "reload_elapsed = 0.0", "reload_sound.stop()"]:
            self.assertIn(marker, refill)

    def test_runtime_qa_covers_reload_swap_and_last_stand(self):
        for marker in ["a cancelled reload callback must not transfer ammunition",
                       "partial reload must consume only remaining reserve ammunition",
                       "weapon swap must not bypass previous shotgun-rate cooldown",
                       "last stand must reject a non-pistol weapon"]:
            self.assertIn(marker, self.runtime)

    def test_ui_return_holds_fire_until_mouse_is_released(self):
        for func_name in ["_on_game_start", "_on_resume", "_close_shop"]:
            segment = self.main.split(f"func {func_name}(", 1)[1].split("\nfunc ", 1)[0]
            self.assertIn(
                "player.suppress_fire_until_release = Input.is_mouse_button_pressed(MOUSE_BUTTON_LEFT)",
                segment,
            )

    def test_sprint_qa_uses_float_easing_not_boolean(self):
        self.assertIn("game.player._animate_viewmodel(0.18, 1.0)", self.runtime)
        self.assertIn("game.player._animate_viewmodel(0.18, 0.0)", self.runtime)
        self.assertNotIn("_animate_viewmodel(0.18, true)", self.runtime)
        self.assertNotIn("_animate_viewmodel(0.18, false)", self.runtime)


if __name__ == "__main__":
    unittest.main()
