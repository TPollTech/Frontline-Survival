"""Geometric regression of decorative first-person sniper sights.
Runs the actual original game mesh generator without overwriting shipped assets.
"""
import unittest
from unittest.mock import patch
from pathlib import Path
import sys

import numpy as np
from scipy.spatial import ConvexHull

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
import build_weapons as models

CASES = {
    'sniper': [
        ('receiver_rail', 'fixed_rear_bridge', ('iron_rear_sight',)),
        ('precision_barrel', 'fixed_front_bridge', ('iron_front_guard', 'iron_front_post')),
    ],
    'bolt_sniper': [
        ('receiver_sight_rail', 'fixed_rear_bridge', ('iron_rear_notch',)),
        ('fixed_front_sight_base', 'fixed_front_bridge', ('iron_front_wing', 'iron_front_blade')),
    ],
    'sentinela': [
        ('receiver', 'fixed_rear_bridge', ('sight_notch',)),
        ('barrel', 'fixed_front_bridge', ('sight_post',)),
    ],
}

def parts(gun, name):
    return [mesh for key, mesh in gun.scene.geometry.items()
            if key.rsplit('_', 1)[0] == name]

def intersects(a, b):
    lo = np.maximum(a.bounds[0], b.bounds[0])
    hi = np.minimum(a.bounds[1], b.bounds[1])
    if np.any(hi - lo <= 1e-6):
        return False
    # Require a common strictly interior sample, not just overlapping AABBs.
    axes = [np.linspace(l, h, 9)[1:-1] for l, h in zip(lo, hi)]
    samples = np.stack(np.meshgrid(*axes, indexing='ij'), axis=-1).reshape(-1, 3)
    def inside(mesh):
        planes = ConvexHull(mesh.vertices).equations
        return np.all(samples @ planes[:, :3].T + planes[:, 3] < -1e-6, axis=1)
    return bool(np.any(inside(a) & inside(b)))

class SniperSightGeometryTests(unittest.TestCase):
    def capture(self, name):
        captured = []
        with patch.object(models.Gun, 'save', lambda gun, _: captured.append(gun)):
            getattr(models, name)()
        self.assertEqual(len(captured), 1)
        return captured[0]

    def test_all_sights_connected_to_static_mesh(self):
        for name, connections in CASES.items():
            gun = self.capture(name)
            for parent_name, bridge_name, child_names in connections:
                with self.subTest(weapon=name, bridge=bridge_name):
                    parent, = parts(gun, parent_name)
                    bridge, = parts(gun, bridge_name)
                    self.assertTrue(bridge.is_watertight)
                    self.assertGreater(bridge.volume, 0)
                    self.assertTrue(intersects(parent, bridge))
                    for child_name in child_names:
                        children = parts(gun, child_name)
                        self.assertTrue(children)
                        for child in children:
                            self.assertTrue(intersects(bridge, child), child_name)
                            self.assertTrue(any(child is x for x in gun.groups['body']))
                    self.assertTrue(any(bridge is x for x in gun.groups['body']))

    def test_rear_visual_edges_match_front_tip(self):
        for name, rear, front in [
            ('sniper', 'iron_rear_sight', 'iron_front_post'),
            ('bolt_sniper', 'iron_rear_notch', 'iron_front_blade'),
            ('rifle', 'iron_sight_notch', 'iron_sight_post'),
        ]:
            gun = self.capture(name)
            front_mesh, = parts(gun, front)
            for rear_mesh in parts(gun, rear):
                self.assertAlmostEqual(rear_mesh.bounds[1, 1], front_mesh.bounds[1, 1], places=6)

    def test_aim_height_matches_front_mesh_and_snapshot(self):
        source = (ROOT / 'scripts/player.gd').read_text(encoding='utf-8')
        snapshot = (ROOT / 'tests/viewmodel_qa_snapshot.gd').read_text(encoding='utf-8')
        for name, tip, height in [('sniper', 'iron_front_post', .1935),
                                  ('bolt_sniper', 'iron_front_blade', .196),
                                  ('sentinela', 'sight_post', .17)]:
            with self.subTest(weapon=name):
                mesh, = parts(self.capture(name), tip)
                self.assertAlmostEqual(mesh.bounds[1, 1], height, places=6)
                self.assertIn(str(height), source.split('func get_sight_height()', 1)[1].split('\nfunc ', 1)[0])
        self.assertIn('game.player.get_viewmodel_rest_pose(ads)', snapshot)
        self.assertIn('-viewmodel_scale * get_sight_height()', source)

if __name__ == '__main__':
    unittest.main()
