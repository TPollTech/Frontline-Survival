"""Bake the organic FPS recipes into joint-local mesh templates."""
import json
from pathlib import Path

from tools.asset_pipeline.parametric.fps_hand_geometry import (
    dorsal_panel, finger_segment, palm, sleeve,
)


def template(build):
    short = build(0.1)
    long = build(1.1)
    assert short.triangles == long.triangles
    vertices = []
    for (x, y, z), (_, far_y, _) in zip(short.vertices, long.vertices):
        slope = far_y - y
        vertices.append((x, y - 0.1 * slope, z, slope))
    return [vertices, short.triangles]


def main():
    recipes = {
        "palm_right": lambda _: palm(True),
        "palm_left": lambda _: palm(False),
        "panel": lambda _: dorsal_panel(),
        "upper": lambda length: sleeve("upper", length, .068, .075),
        "forearm": lambda length: sleeve("forearm", length, .052, .063),
        "cuff": lambda length: sleeve("cuff", length, .054, .062),
    }
    for digit in range(5):
        for distal in (False, True):
            recipes[f"digit_{digit}_{int(distal)}"] = (
                lambda length, digit=digit, distal=distal: finger_segment(digit, distal, length)
            )
    root = Path(__file__).resolve().parents[2]
    target = root / "assets/models/fps_hand_templates.json"
    target.write_text(json.dumps({key: template(value) for key, value in recipes.items()},
                                 separators=(",", ":")) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
