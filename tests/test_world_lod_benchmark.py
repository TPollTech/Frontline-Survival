"""Synthetic verifier tests only; these are not measured performance results."""
import unittest
from tools.asset_pipeline.world_lod_benchmark import FRAMES, ORDER, summarize


def fixture():
    runs = []
    for mode in ORDER:
        fixed = mode == "fixed_lod0"
        runs.append({"mode": mode, "frame_ms": [20.0 if fixed else 10.0] * FRAMES,
                     "registered_triangles": [49248] * FRAMES if fixed else [12000, 14000] * (FRAMES // 2)})
    return {"kind": "world_lod_benchmark", "schema_version": 1, "resolution": [1280, 720],
            "warmup_frames": FRAMES, "assemblies": 23, "scope": "frozen_map_camera_route",
            "hardware_validated": False, "vsync_disabled": True, "cpu": "synthetic", "gpu": "synthetic",
            "os": "synthetic", "godot_version": "synthetic", "runs": runs}


class BenchmarkVerifier(unittest.TestCase):
    def test_summary(self):
        result = summarize(fixture())
        self.assertEqual([p["fps_from_intervals"] for p in result["passes"]], [50, 100, 100, 50])
        self.assertEqual(result["passes"][1]["mean_registered_triangles"], 13000)
        self.assertFalse(result["hardware_validated"])

    def test_percentile(self):
        data = fixture()
        data["runs"][0]["frame_ms"] = list(range(1, FRAMES + 1))
        result = summarize(data)["passes"][0]
        self.assertEqual(result["p95_ms"], 228)
        self.assertEqual(result["p99_ms"], 238)
        self.assertEqual(result["median_ms"], 120.5)

    def test_pass_order(self):
        data = fixture(); data["runs"].reverse(); data["runs"][0]["mode"] = "automatic"
        with self.assertRaisesRegex(ValueError, "pass order"): summarize(data)

    def test_sample_count(self):
        data = fixture(); data["runs"][0]["frame_ms"].pop()
        with self.assertRaisesRegex(ValueError, "sample count"): summarize(data)

    def test_nonfinite(self):
        data = fixture(); data["runs"][0]["frame_ms"][0] = float("nan")
        with self.assertRaisesRegex(ValueError, "invalid frame intervals"): summarize(data)

    def test_fixed_baseline(self):
        data = fixture(); data["runs"][0]["registered_triangles"][0] = 12345
        with self.assertRaisesRegex(ValueError, "fixed baseline changed"): summarize(data)

    def test_no_lod_change(self):
        data = fixture(); data["runs"][1]["registered_triangles"] = [49248] * FRAMES
        with self.assertRaisesRegex(ValueError, "automatic LOD did not vary"): summarize(data)

    def test_no_hardware_approval(self):
        data = fixture(); data["hardware_validated"] = True
        with self.assertRaisesRegex(ValueError, "benchmark flags"): summarize(data)


if __name__ == "__main__":
    unittest.main()
