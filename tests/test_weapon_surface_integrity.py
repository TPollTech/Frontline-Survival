"""Geometry regressions for cosmetic solids and known disconnected details."""
import unittest
from test_sniper_sight_geometry import SniperSightGeometryTests, parts, intersects
import numpy as np
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

class SurfaceIntegrityTests(unittest.TestCase):
    def capture(self, name):
        return SniperSightGeometryTests().capture(name)

    def test_all_original_solids_have_valid_geometry(self):
        for name in ('pistol', 'smg', 'rifle', 'shotgun', 'lmg', 'sentinela', 'sniper', 'bolt_sniper'):
            with self.subTest(weapon=name):
                gun = self.capture(name)
                gun.validate_geometry()

    def test_cosmetic_bridges_connect_to_parent_and_child(self):
        for name, parent, bridge, child in (
            ('smg', 'top_rail', 'fixed_optic_bridge', 'optic_mount'),
            ('lmg', 'top_rail', 'fixed_optic_bridge', 'optic_mount'),
            ('shotgun', 'upper_barrel', 'fixed_bead_base', 'bead_sight'),
        ):
            with self.subTest(weapon=name):
                gun = self.capture(name)
                parent_mesh, = parts(gun, parent)
                bridge_mesh, = parts(gun, bridge)
                child_mesh, = parts(gun, child)
                self.assertTrue(intersects(parent_mesh, bridge_mesh))
                self.assertTrue(intersects(bridge_mesh, child_mesh))

    def test_rifle_sight_contacts_preserve_reference_height(self):
        gun = self.capture('rifle')
        post, = parts(gun, 'iron_sight_post')
        front, = parts(gun, 'front_block')
        rear, = parts(gun, 'fixed_rifle_rear_base')
        self.assertTrue(intersects(post, front))
        self.assertAlmostEqual(post.bounds[1, 1], .177, places=6)
        self.assertTrue(all(intersects(rear, notch) for notch in parts(gun, 'iron_sight_notch')))

    def test_solid_material_and_intentional_transparent_lens(self):
        player = (ROOT / 'scripts/player.gd').read_text(encoding='utf-8')
        materials = (ROOT / 'scripts/weapon_materials.gd').read_text(encoding='utf-8')
        self.assertIn('material.transparency = BaseMaterial3D.TRANSPARENCY_DISABLED', materials)
        self.assertIn('glass_material.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA', player)
        self.assertIn('glass.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF', player)

if __name__ == '__main__':
    unittest.main()
