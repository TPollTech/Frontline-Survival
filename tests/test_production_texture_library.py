"""Round-trip checks of 02-05 maps through the canonical PBR library."""
import hashlib
import json
from pathlib import Path
import struct
import tempfile
import unittest
import zlib

from tools.asset_pipeline.parametric.production_texture_maps import build_library

ROOT = Path(__file__).resolve().parents[1]
PROFILES = json.loads((ROOT / "tools/asset_pipeline/parametric/production_surface_profiles.json")
                      .read_text(encoding="utf-8"))["profiles"]


class TextureLibraryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.library = build_library(PROFILES, 256, 205)

    def test_material_bindings(self):
        self.assertEqual({m.id for m in self.library.materials}, set(PROFILES))
        self.assertEqual(len(self.library.textures), 18)
        by_id = {t.id: t for t in self.library.textures}
        for m in self.library.materials:
            self.assertEqual((m.metallic, m.roughness), (1., 1.))
            self.assertEqual(m.base_color, (1., 1., 1., 1.))
            self.assertEqual(m.alpha_mode, "OPAQUE")
            self.assertEqual(set(m.texture_slots()), {"base_color", "normal", "orm"})
            for role, id in m.texture_slots().items():
                self.assertEqual(id, m.id + "_" + role)
                self.assertEqual(by_id[id].role, role)

    def test_manifest_provenance_and_channels(self):
        manifest = self.library.manifest()
        self.assertEqual(manifest["normal_convention"], "+Y")
        self.assertEqual(manifest["orm_channels"], {"R": "occlusion", "G": "roughness", "B": "metallic"})
        for t in manifest["textures"]:
            self.assertEqual(t["color_space"], "sRGB" if t["role"] == "base_color" else "linear")
            self.assertEqual(t["license"], "CC0-1.0")
            self.assertTrue(t["source"].startswith("procedural:frontline-02-05:"))
            self.assertEqual((t["width"], t["height"]), (256, 256))

    def test_png_roundtrip_and_hashes(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.library.write(root)
            self.assertTrue(self.library.verify(root))
            for t in self.library.textures:
                data = (root / t.metadata()["path"]).read_bytes()
                self.assertEqual(data[:8], b"\x89PNG\r\n\x1a\n")
                self.assertEqual(hashlib.sha256(data).hexdigest(), t.metadata()["sha256"])
                offset, compressed = 8, bytearray()
                while offset < len(data):
                    size = struct.unpack_from(">I", data, offset)[0]
                    kind = data[offset+4:offset+8]
                    body = data[offset+8:offset+8+size]
                    self.assertEqual(struct.unpack_from(">I", data, offset+8+size)[0], zlib.crc32(kind+body))
                    if kind == b"IHDR":
                        self.assertEqual(struct.unpack(">IIBBBBB", body), (256, 256, 8, 2, 0, 0, 0))
                    if kind == b"IDAT":
                        compressed.extend(body)
                    offset += size + 12
                raw = zlib.decompress(compressed)
                stride = 256*3+1
                self.assertEqual(len(raw), stride*256)
                self.assertTrue(all(raw[i] == 0 for i in range(0, len(raw), stride)))
                pixels = b"".join(raw[i+1:i+stride] for i in range(0, len(raw), stride))
                self.assertEqual(pixels, t.rgb)
                self.assertEqual(hashlib.sha256(pixels).hexdigest(), t.metadata()["pixel_sha256"])

    def test_library_determinism(self):
        other = build_library(dict(reversed(list(PROFILES.items()))), 256, 205)
        self.assertEqual(other.canonical_json(), self.library.canonical_json())
        self.assertEqual(other.textures, self.library.textures)

    def test_fail_closed_on_tampering_and_overwrite(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.library.write(root)
            with self.assertRaises(ValueError):
                self.library.write(root)
            target = root / self.library.textures[0].metadata()["path"]
            original = target.read_bytes()
            target.write_bytes(original[:-1])
            with self.assertRaises(ValueError):
                self.library.verify(root)
            target.write_bytes(original)
            target.unlink()
            with self.assertRaises(ValueError):
                self.library.verify(root)

    def test_reject_invalid_configuration(self):
        for seed in (-1, 2**32, True, 1.5):
            with self.subTest(seed=seed), self.assertRaises(ValueError):
                build_library(PROFILES, 64, seed)
        for size in (64.0, 65, True):
            with self.subTest(size=size), self.assertRaises(ValueError):
                build_library(PROFILES, size, 205)
        with self.assertRaises(ValueError):
            build_library({}, 64, 205)
