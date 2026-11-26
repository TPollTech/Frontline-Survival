"""02-01 hybrid authoring contract for the production pistol.

The pistol mixes legacy machined chamfers with one sculpted surface produced by
the central parametric library. These checks protect the demonstration asset
without regenerating the shipped GLBs: the source is built in memory and the
grouped exports are written to a temporary directory only.
"""
import hashlib
import json
import struct
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
sys.path.insert(0, str(ROOT / 'tests'))
import build_weapons as models
from test_sniper_sight_geometry import parts, intersects

# Provisional LOD0 ceiling for the weapon category (docs/GUIA_PIPELINE_3D.md).
WEAPON_LOD0_TRIANGLES = 18000
EXPECTED_PART_GROUPS = {'body': 23, 'action': 22, 'mag': 2}
EXPECTED_GRIP_TRIANGLES = 1200


def build(name, out):
    Path(out).mkdir(parents=True, exist_ok=True)
    captured = {}
    original = models.Gun.save

    def save(gun, gun_name):
        captured[gun_name] = gun
        return original(gun, gun_name)

    with patch.object(models, 'OUT', Path(out)), patch.object(models.Gun, 'save', save):
        models.RECIPES[name]()
    return captured[name]


def glb_attributes(path):
    data = Path(path).read_bytes()
    json_length, = struct.unpack('<I', data[12:16])
    document = json.loads(data[20:20 + json_length])
    attributes = document['meshes'][0]['primitives'][0]['attributes']
    return set(attributes)


class HybridPistolTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.out = Path(self.tmp.name) / 'a'
        self.gun = build('pistol', self.out)

    def test_source_uses_central_parametric_loft(self):
        source = (ROOT / 'tools/build_weapons.py').read_text(encoding='utf-8')
        self.assertIn('from asset_pipeline.parametric.organic import', source)
        self.assertIn('OrganicLoft(', source)
        self.assertIn('hybrid_pistol_grip(g)', source)

    def test_sculpted_grip_is_a_closed_solid_in_the_body_group(self):
        grip, = parts(self.gun, 'grip')
        self.assertEqual(len(grip.faces), EXPECTED_GRIP_TRIANGLES)
        self.assertTrue(grip.is_watertight)
        self.assertTrue(np.isfinite(grip.vertices).all())
        self.assertGreater(float(grip.volume), 0.0)
        self.assertIn(grip, self.gun.groups['body'])

    def test_grip_keeps_frame_and_heel_contacts(self):
        grip, = parts(self.gun, 'grip')
        frame, = parts(self.gun, 'frame')
        heel, = parts(self.gun, 'grip_heel')
        self.assertTrue(intersects(grip, frame), 'grip must meet the frame')
        self.assertTrue(intersects(grip, heel), 'grip must meet the magazine heel')

    def test_part_groups_and_envelope_are_preserved(self):
        self.assertEqual(self.gun.count, 47)
        self.assertEqual({key: len(value) for key, value in self.gun.groups.items()},
                         EXPECTED_PART_GROUPS)
        bounds = np.array([mesh.bounds for mesh in self.gun.scene.geometry.values()])
        lo = bounds[:, 0, :].min(axis=0)
        hi = bounds[:, 1, :].max(axis=0)
        # Measured envelope of the shared production contract of the standard
        # (docs/PADRAO_ARTISTICO_3D.md); 1 mm tolerance absorbs float noise only.
        np.testing.assert_allclose(hi - lo, [0.1188, 0.3875, 0.393], atol=1e-3)
        self.assertLessEqual(hi[2], 0.106 + 1e-6)
        self.assertGreaterEqual(lo[1], -0.266 - 1e-6)

    def test_budget_and_exported_attributes(self):
        triangles = sum(len(mesh.faces) for mesh in self.gun.scene.geometry.values())
        self.assertLessEqual(triangles, WEAPON_LOD0_TRIANGLES)
        merged = self.out / 'pistol.glb'
        self.assertTrue(merged.is_file())
        self.assertEqual(glb_attributes(merged), {'POSITION', 'COLOR_0', 'NORMAL', 'TANGENT'})

    def test_two_generations_are_byte_identical(self):
        second = Path(self.tmp.name) / 'b'
        build('pistol', second)
        for name in ('pistol.glb', 'pistol_body.glb', 'pistol_action.glb', 'pistol_mag.glb'):
            first = hashlib.sha256((self.out / name).read_bytes()).hexdigest()
            again = hashlib.sha256((second / name).read_bytes()).hexdigest()
            self.assertEqual(first, again, name)


if __name__ == '__main__':
    unittest.main()
