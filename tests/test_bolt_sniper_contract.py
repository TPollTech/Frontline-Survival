"""Mechanical VLR-8 rifle regression contracts; Godot tests gameplay state."""
from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[1]
PLAYER=(ROOT/"scripts/player.gd").read_text(encoding="utf-8")
MAIN=(ROOT/"scripts/main.gd").read_text(encoding="utf-8")
MODEL=(ROOT/"tools/build_weapons.py").read_text(encoding="utf-8")
AUDIO=(ROOT/"scripts/weapon_audio.gd").read_text(encoding="utf-8")
QA=(ROOT/"tests/runtime_wave_qa.gd").read_text(encoding="utf-8")

def body(src,name):
    return src.split(f"func {name}(",1)[1].split("\nfunc ",1)[0]

class VLR8BoltSniperContracts(unittest.TestCase):
    def test_original_mrs7_is_preserved(self):
        self.assertIn('"sniper": {"name":"Fuzil de Precisao MRS-7"', PLAYER)
        self.assertIn('["MRS-7 Sniper (iron sight)", 1600, "sniper"]',MAIN)
        self.assertIn("def sniper():",MODEL)

    def test_distinct_vlr8_stats_and_glb(self):
        self.assertIn('"bolt_sniper": {"name":"VLR-8 Ferrolho"',PLAYER)
        for expected in ('"damage":215.0','"mag":5','"reserve":20','"rate":1.90','"reload":3.25'):
            self.assertIn(expected,PLAYER)
        self.assertIn("def bolt_sniper():",MODEL)
        self.assertIn("g.save('bolt_sniper')",MODEL)
        self.assertIn("charging_handle_bolt_body",MODEL)

    def test_separate_weapon_station_purchase(self):
        self.assertIn('["VLR-8 Sniper Bolt Action (iron sight)", 1800, "bolt_sniper"]',MAIN)
        self.assertIn('"sniper", "bolt_sniper"] and player.owned_weapons.has(id)',MAIN)

    def test_mechanical_chamber_prevents_double_fire(self):
        shot=body(PLAYER,"shoot")
        self.assertIn('weapon_id == "bolt_sniper" and bolt_cycle_remaining > 0.0',shot)
        self.assertIn('bolt_cycle_remaining = BOLT_CYCLE_SECONDS',shot)
        self.assertLess(shot.index('if weapon_id == "bolt_sniper" and bolt_cycle_remaining'),shot.index("magazines[weapon_id] -= 1"))

    def test_cycle_is_advanced_not_skipped_by_weapon_swap(self):
        self.assertIn("_advance_bolt_cycle(delta)",body(PLAYER,"_physics_process"))
        self.assertIn("maxf(0.0, bolt_cycle_remaining - delta)",body(PLAYER,"_advance_bolt_cycle"))
        self.assertNotIn("bolt_cycle_remaining = 0.0",body(PLAYER,"switch_weapon"))

    def test_mechanical_animation_is_not_fake_rate_only(self):
        animate=body(PLAYER,"_animate_viewmodel")
        self.assertIn("bolt_pull",animate)
        self.assertIn("bolt_lift",animate)
        self.assertIn("action_part.rotation.z",animate)
        self.assertIn("cycling += 0.26 * bolt_pull",animate)

    def test_magazine_reload_chambers_and_conserves(self):
        self.assertIn('if weapon_id == "bolt_sniper":',body(PLAYER,"start_reload"))
        self.assertIn("bolt_cycle_remaining = 0.0",body(PLAYER,"start_reload"))
        self.assertIn("var loaded: int = mini(needed, reserves[weapon_id])",body(PLAYER,"_finish_reload"))

    def test_real_wav_sound_for_bolt_not_scripted(self):
        self.assertIn('bolt_sound.stream = WeaponAudio.reload_for("rifle")',PLAYER)
        self.assertIn('bolt_sound.play()',body(PLAYER,"_advance_bolt_cycle"))
        self.assertIn('"bolt_sniper": preload("res://assets/audio/weapons/rifle.wav")',AUDIO)

    def test_scope_purchase_is_independent_across_rifles(self):
        self.assertIn('weapon_attachments.get(weapon_id, {})',body(PLAYER,"_sniper_scope"))
        self.assertIn('weapon_id not in ["sniper", "bolt_sniper"]',body(MAIN,"_shop_optic_block_reason"))
        self.assertIn("VLR-8 scope must survive switching",QA)

    def test_integration_covers_actual_firing_and_cycling(self):
        for msg in ("VLR-8 first shot must open the bolt", "bolt-action firing cannot bypass",
                    "bolt mesh must physically retract", "weapon swapping must not reset incomplete bolt cycling",
                    "VLR-8 must fire again after the bolt closes", "bolt-action reload must conserve spare ammunition"):
            self.assertIn(msg,QA)

if __name__=="__main__":
    unittest.main()
