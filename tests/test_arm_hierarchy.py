"""Static checks for the articulated first-person arm hierarchy.
These cannot substitute for Windows animation and geometry inspection.
"""
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
SRC = (ROOT / "scripts/player.gd").read_text(encoding="utf-8")
QA = (ROOT / "tests/runtime_wave_qa.gd").read_text(encoding="utf-8")


class ArmHierarchyTests(unittest.TestCase):
    def func(self, name):
        return SRC.split(f"func {name}(", 1)[1].split("\nfunc ", 1)[0]

    def test_shoulder_elbow_wrist_nodes(self):
        body = self.func("_add_first_person_arm")
        for name in ('"TriggerShoulder"', '"SupportShoulder"', '"Elbow"', '"Wrist"'):
            self.assertIn(name, body)
        self.assertIn("shoulder_joint.add_child(elbow_joint)", body)
        self.assertIn("elbow_joint.add_child(wrist_joint)", body)

    def test_palm_and_bent_two_segment_fingers(self):
        body = self.func("_add_first_person_arm")
        for name in ('"Palm"', '"Finger%dProximal"', '"Finger%dDistal"',
                     '"ThumbProximal"', '"ThumbDistal"'):
            self.assertIn(name, body)
        self.assertIn("for finger in range(4):", body)

    def test_proximal_and_distal_fingers_have_independent_pivots(self):
        body = self.func("_add_first_person_arm")
        for marker in ("knuckle_joint.position = knuckle",
                       "wrist_joint.add_child(knuckle_joint)",
                       "knuckle_joint.add_child(tip_joint)",
                       "trigger_finger_knuckles.append(knuckle_joint)",
                       "support_finger_tips.append(tip_joint)"):
            self.assertIn(marker, body)
        self.assertIn("middle - knuckle", body)
        self.assertIn("fingertip - middle", body)

    def test_weapon_rebuild_clears_both_finger_arrays(self):
        build = self.func("_update_gun_mesh")
        for name in ("trigger_finger_knuckles", "trigger_finger_tips",
                     "support_finger_knuckles", "support_finger_tips"):
            self.assertIn(name + ".clear()", build)

    def test_neutral_material_is_reused(self):
        body = self.func("_arm_piece")
        self.assertIn("if not arm_materials.has(material_key):", body)
        self.assertIn("part.material_override = arm_materials[material_key]", body)

    def test_weapon_rebuild_drops_old_joint_refs(self):
        body = self.func("_update_gun_mesh")
        for field in ("trigger_elbow_joint", "trigger_wrist_joint",
                      "support_elbow_joint", "support_wrist_joint"):
            self.assertIn(f"{field} = null", body)

    def test_trigger_elbow_and_wrist_follow_recoil_equip_melee(self):
        body = self.func("_animate_viewmodel")
        for mark in ("trigger_elbow_joint.rotation.x", "trigger_wrist_joint.rotation.z",
                     "shot_anim", "equip_tilt", "melee_punch"):
            self.assertIn(mark, body)

    def test_support_elbow_and_wrist_follow_reload_sprint(self):
        body = self.func("_animate_viewmodel")
        for mark in ("support_elbow_joint.rotation.x", "support_wrist_joint.rotation.z",
                     "mag_out", "pump", "sprint_ease"):
            self.assertIn(mark, body)

    def test_integration_covers_all_five_weapons(self):
        self.assertIn('for gun_id: String in ["pistol", "smg", "rifle", "shotgun", "lmg"]:', QA)
        self.assertIn("gloved fingers/knuckles are incomplete for", QA)
        self.assertIn("trigger elbow must return to neutral", QA)


if __name__ == "__main__":
    unittest.main()
