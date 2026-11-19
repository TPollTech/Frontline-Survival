"""MRS-7 sniper integration contracts: staged scopes, ADS, weapon model and sound.

The integration test executes actual in-engine purchases, reload and ADS logic.
Manual Windows playtesting remains required for sight alignment and feel.
"""
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
PLAYER = (ROOT / "scripts/player.gd").read_text(encoding="utf-8")
MAIN = (ROOT / "scripts/main.gd").read_text(encoding="utf-8")
MODEL = (ROOT / "tools/build_weapons.py").read_text(encoding="utf-8")
AUDIO = (ROOT / "scripts/weapon_audio.gd").read_text(encoding="utf-8")
QA = (ROOT / "tests/runtime_wave_qa.gd").read_text(encoding="utf-8")


def body(source, func):
    return source.split(f"func {func}(", 1)[1].split("\nfunc ", 1)[0]


class MRS7SniperContracts(unittest.TestCase):
    def test_has_real_sniper_stats_and_separate_magazine(self):
        self.assertIn('"sniper": {"name":"Fuzil de Precisao MRS-7"', PLAYER)
        for expected in ('"mag":5', '"reserve":25', '"rate":1.35', '"reload":2.90', '"auto":false'):
            self.assertIn(expected, PLAYER)

    def test_model_generator_exports_sniper_with_mechanical_parts(self):
        self.assertIn("def sniper():", MODEL)
        self.assertIn("g.save('sniper')", MODEL)
        self.assertIn("name='magazine_box'", MODEL)
        self.assertIn("name='charging_handle'", MODEL)
        self.assertIn("iron_front_post", MODEL)
        self.assertIn("shotgun();lmg();sniper()", MODEL)

    def test_scope_purchase_stays_inside_weapon_station(self):
        for value in ('["MRS-7 Sniper (iron sight)", 1600, "sniper"]',
                      '["Luneta 2x da sniper", 650, "scope_2x"]',
                      '["Luneta 4x da sniper (exige 2x)", 1000, "scope_4x"]'):
            self.assertIn(value, MAIN)

    def test_scope_sequence_prevents_bypass_and_downgrade(self):
        install = body(PLAYER, "install_attachment")
        self.assertIn('id not in ["scope_2x", "scope_4x"]', install)
        self.assertIn('previous_scope == "scope_4x"', install)
        self.assertIn('id == "scope_4x" and previous_scope != "scope_2x"', install)
        self.assertIn("EQUIPE SNIPER", body(MAIN, "_shop_optic_block_reason"))
        self.assertIn("EXIGE LUNETA 2X", body(MAIN, "_shop_optic_block_reason"))

    def test_invalid_upgrade_never_debits_wallet(self):
        buy = body(MAIN, "_buy")
        self.assertIn("var optic_block_reason: String = _shop_optic_block_reason(id)", buy)
        self.assertLess(buy.index("var optic_block_reason:"), buy.index("wallet -= price"))

    def test_ads_zoom_irons_and_scope_sensitivity(self):
        fov = body(PLAYER, "_ads_fov_multiplier")
        for value in ("return 0.70", "return 0.48", "return 0.29"):
            self.assertIn(value, fov)
        self.assertIn("scope_sensitivity = 0.42", body(PLAYER, "_input"))
        self.assertIn("_ads_fov_multiplier() if aim", body(PLAYER, "_physics_process"))

    def test_quickscope_precision_and_hipfire_penalty(self):
        shot = body(PLAYER, "_sniper_shot_spread")
        self.assertIn("if not aim:", shot)
        self.assertIn("sniper_ads_seconds < 0.11", shot)
        self.assertIn("return 0.13", shot)
        self.assertIn("return 0.045", shot)
        self.assertIn("return 0.0012", shot)
        self.assertIn("spread = _sniper_shot_spread()", body(PLAYER, "shoot"))

    def test_real_3d_scope_and_bolt_action_motion(self):
        model = body(PLAYER, "_build_sniper_scope")
        self.assertIn("TorusMesh.new()", model)
        self.assertIn("Scope_HollowRing", model)
        self.assertIn("Optic_EmissiveReticle", model)
        self.assertIn('optic.begins_with("scope_")', body(PLAYER, "_build_attachment_models"))
        self.assertIn('cycling = 0.12 * shot_anim', body(PLAYER, "_animate_viewmodel"))

    def test_recorded_wav_not_generated_beeps(self):
        self.assertIn('"sniper": preload("res://assets/audio/weapons/rifle.wav")', AUDIO)
        self.assertIn('"sniper": preload("res://assets/audio/reloads/rifle.wav")', AUDIO)
        self.assertIn('shot_sound.pitch_scale = 0.64 if weapon_id == "bolt_sniper" else (0.76 if weapon_id == "sniper"', PLAYER)

    def test_integration_checks_all_purchase_and_quick_scope_paths(self):
        for marker in ("sniper did not start with iron sights",
                       "4x scope bypassed required 2x progression",
                       "paid 2x optic missing or not installed",
                       "paid 4x optic missing or not installed",
                       "scope downgrade charged credits",
                       "quick scope timing must reward 110ms ADS",
                       "sniper reload must transfer only five available rounds",
                       "upgraded sniper scope lost after weapon switch"):
            self.assertIn(marker, QA)


if __name__ == "__main__":
    unittest.main()
