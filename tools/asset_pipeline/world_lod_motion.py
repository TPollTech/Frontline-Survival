"""Check motion evidence consistency; PNG headers and traces are not visual approval."""
from collections import Counter
import math
import struct

STEPS_PER_SIDE = 110
FRAME_COUNT = STEPS_PER_SIDE * 4 + 1
CORNERS = ((-22, -22), (22, -22), (22, 22), (-22, 22))
FAMILIES = {"barricade": 4, "container_corners": 4, "barrel": 8, "shop": 3, "light_post": 4}


def require(ok, message):
    if not ok:
        raise ValueError(message)


def expected_position(index):
    segment, step = divmod(index % (FRAME_COUNT - 1), STEPS_PER_SIDE)
    start, end = CORNERS[segment], CORNERS[(segment + 1) % 4]
    weight = step / STEPS_PER_SIDE
    return [start[0] + (end[0] - start[0]) * weight, 1.65,
            start[1] + (end[1] - start[1]) * weight]


def verify_motion(report, directory):
    require(report.get("kind") == "world_lod_motion" and report.get("schema_version") == 1, "motion schema")
    require(report.get("resolution") == [1280, 720] and report.get("simulated_delta_s") == 0.1, "motion settings")
    require(report.get("visual_reviewed") is False and report.get("hardware_validated") is False, "unexpected approval")
    assemblies = report["assemblies"]
    require(Counter(a["family"] for a in assemblies) == Counter(FAMILIES), "motion family coverage")
    require(all(isinstance(a["path"], str) and a["path"] for a in assemblies) and len({a["path"] for a in assemblies}) == 23, "motion assembly paths")
    frames = report["frames"]
    require(len(frames) == FRAME_COUNT, "motion frame count")
    transitions = Counter()
    previous = None
    for i, frame in enumerate(frames):
        require(frame["index"] == i and frame["file"] == f"motion-{i:04d}.png", "motion frame identity")
        pos = frame["camera_m"]
        require(len(pos) == 3 and all(type(v) in (int, float) and math.isfinite(v) and abs(v - want) < 0.001 for v, want in zip(pos, expected_position(i))), "motion camera path")
        levels = frame["levels"]
        require(len(levels) == 23 and all(type(v) is int and 0 <= v <= 2 for v in levels), "motion levels")
        if previous is not None:
            for a, before, after in zip(assemblies, previous, levels):
                if before != after:
                    require(abs(before - after) == 1, "motion skipped LOD")
                    transitions[(a["family"], before, after)] += 1
        previous = levels
        path = directory / frame["file"]
        with path.open("rb") as stream:
            header = stream.read(24)
        require(len(header) == 24 and header[:16] == b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR" and struct.unpack(">II", header[16:]) == (1280, 720) and path.stat().st_size > 33, "motion PNG header")
    require({(before, after) for _, before, after in transitions} == {(0, 1), (1, 0), (1, 2), (2, 1)}, "motion transition coverage")
    return {"frames": FRAME_COUNT, "capture_headers_checked": FRAME_COUNT,
            "transitions": [{"family": family, "from": before, "to": after, "count": count}
                            for (family, before, after), count in sorted(transitions.items())],
            "visual_reviewed": False, "hardware_validated": False,
            "limitations": ["Simulated camera motion, not gameplay", "PNG headers only, not image decoding", "No FPS measurement or visual approval"]}
