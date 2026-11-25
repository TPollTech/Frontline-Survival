"""Validate and summarize measured frame intervals from the isolated LOD QA."""
import math
import statistics

ORDER = ("fixed_lod0", "automatic", "automatic", "fixed_lod0")
FRAMES = 240
LOD0_TRIANGLES = 49248


def require(condition, message):
    if not condition:
        raise ValueError(message)


def summarize(report):
    require(report.get("kind") == "world_lod_benchmark" and report.get("schema_version") == 1, "benchmark schema")
    require(report.get("resolution") == [1280, 720] and report.get("warmup_frames") == FRAMES, "benchmark configuration")
    require(report.get("assemblies") == 23 and report.get("scope") == "frozen_map_camera_route", "benchmark scope")
    require(report.get("hardware_validated") is False and report.get("vsync_disabled") is True, "benchmark flags")
    for key in ("cpu", "gpu", "os", "godot_version"):
        require(isinstance(report.get(key), str) and bool(report[key].strip()), "missing hardware metadata: " + key)
    runs = report["runs"]
    require(len(runs) == len(ORDER), "pass count")
    results = []
    for mode, run in zip(ORDER, runs):
        require(run["mode"] == mode, "pass order")
        frames = run["frame_ms"]
        triangles = run["registered_triangles"]
        require(len(frames) == len(triangles) == FRAMES, "sample count")
        require(all(type(x) in (int, float) and math.isfinite(x) and x > 0 for x in frames), "invalid frame intervals")
        require(all(type(x) is int and 0 < x <= LOD0_TRIANGLES for x in triangles), "invalid triangle counts")
        if mode == "fixed_lod0":
            require(all(x == LOD0_TRIANGLES for x in triangles), "fixed baseline changed")
        else:
            require(min(triangles) < LOD0_TRIANGLES and len(set(triangles)) > 1, "automatic LOD did not vary")
        ordered = sorted(frames)
        mean = statistics.fmean(frames)
        results.append({"mode": mode, "frames": len(frames), "mean_frame_ms": mean,
                        "fps_from_intervals": 1000 / mean, "median_ms": statistics.median(frames),
                        "p95_ms": ordered[math.ceil(.95 * len(ordered)) - 1],
                        "p99_ms": ordered[math.ceil(.99 * len(ordered)) - 1],
                        "mean_registered_triangles": statistics.fmean(triangles)})
    return {"scope": report["scope"], "hardware": {k: report[k] for k in ("cpu", "gpu", "os", "godot_version")},
            "passes": results, "hardware_validated": False, "visual_reviewed": False,
            "limitations": ["Frozen map, not gameplay", "Frame intervals, not GPU timestamp queries",
                            "Registered geometry, not actual submitted triangles", "No target-hardware approval"]}
