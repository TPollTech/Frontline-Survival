"""Synthetic trace fixtures; no Godot render or performance claims."""
from pathlib import Path
import struct
import tempfile
import unittest
from tools.asset_pipeline.world_lod_motion import FRAME_COUNT, FAMILIES, expected_position, verify_motion


class MotionTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        assemblies = [{"family": family, "path": f"{family}/{i}"} for family, count in FAMILIES.items() for i in range(count)]
        frames = []
        for i in range(FRAME_COUNT):
            name = f"motion-{i:04d}.png"
            (self.root / name).write_bytes(b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR" + struct.pack(">II", 1280, 720) + b"fixture-only")
            level = 0 if i < 100 or i >= 400 else 1 if i < 200 or i >= 300 else 2
            frames.append({"index": i, "file": name, "camera_m": expected_position(i), "levels": [level] * 23})
        self.report = {"kind": "world_lod_motion", "schema_version": 1, "resolution": [1280, 720],
                       "simulated_delta_s": 0.1, "visual_reviewed": False, "hardware_validated": False,
                       "assemblies": assemblies, "frames": frames}

    def verify(self):
        return verify_motion(self.report, self.root)

    def test_valid_fixture(self):
        result = self.verify()
        self.assertEqual(result["frames"], 441)
        self.assertEqual(sum(t["count"] for t in result["transitions"]), 92)
        self.assertFalse(result["visual_reviewed"])

    def test_closed_route(self):
        self.assertEqual(expected_position(0), expected_position(440))
        self.assertEqual(expected_position(110), [22, 1.65, -22])
        self.assertEqual(expected_position(220), [22, 1.65, 22])
        self.assertEqual(expected_position(330), [-22, 1.65, 22])

    def test_missing_frame(self):
        self.report["frames"].pop()
        with self.assertRaisesRegex(ValueError, "frame count"): self.verify()

    def test_wrong_position(self):
        self.report["frames"][10]["camera_m"][0] += 1
        with self.assertRaisesRegex(ValueError, "camera path"): self.verify()

    def test_wrong_identity(self):
        self.report["frames"][1]["file"] = "../other.png"
        with self.assertRaisesRegex(ValueError, "frame identity"): self.verify()

    def test_skipped_level(self):
        self.report["frames"][10]["levels"][0] = 2
        with self.assertRaisesRegex(ValueError, "skipped LOD"): self.verify()

    def test_no_transition(self):
        for f in self.report["frames"]: f["levels"] = [0] * 23
        with self.assertRaisesRegex(ValueError, "transition coverage"): self.verify()

    def test_duplicate_assembly(self):
        self.report["assemblies"][1]["path"] = self.report["assemblies"][0]["path"]
        with self.assertRaisesRegex(ValueError, "assembly paths"): self.verify()

    def test_invalid_capture(self):
        (self.root / "motion-0000.png").write_bytes(b"bad")
        with self.assertRaisesRegex(ValueError, "PNG header"): self.verify()

    def test_false_approval(self):
        self.report["visual_reviewed"] = True
        with self.assertRaisesRegex(ValueError, "unexpected approval"): self.verify()


if __name__ == "__main__":
    unittest.main()
