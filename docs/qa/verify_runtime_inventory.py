"""Verify sampled actual engine inventory; not an artistic approval."""
import json
import math
import sys
from pathlib import Path

IDS = ("pistol", "smg", "rifle", "shotgun", "lmg", "sentinela", "sniper", "bolt_sniper")
def require(condition, message):
    if not condition:
        raise ValueError(message)

def validate(data):
    require(data.get("kind") == "frontline_runtime_inventory" and data.get("schema_version") == 1, "schema")
    require(data.get("coordinate_unit") == "m" and not data.get("failures"), "capture failures or units")
    samples = data["samples"]
    by_id = {s["id"]: s for s in samples}
    require(len(by_id) == len(samples), "duplicate sample")
    for key in ("map_briefing", "ally", "turret", "loot_ammo", "grenade", "grenade_effect", "blood_effect", "combat_visual_event", "enemy_quaternius_experimental"):
        require(key in by_id, "missing sample " + key)
    for weapon in IDS:
        for pose in ("hip", "ads", "reload"):
            require(f"fps_{weapon}___{pose}" in by_id, "missing weapon pose")
        require(f"loot_weapon_{weapon}" in by_id, "missing weapon pickup")
        optics = ("scope_2x", "scope_4x") if weapon in ("sniper", "bolt_sniper") else ("red_dot", "holo")
        if weapon == "sentinela":
            optics += ("scope4",)
        for optic in optics:
            require(f"fps_{weapon}_{optic}__ads" in by_id, "missing optic pose")
        for muzzle in ("suppressor", "compensator"):
            require(f"fps_{weapon}__{muzzle}_hip" in by_id, "missing muzzle pose")
    for sample in samples:
        rows = sample["nodes"]
        paths = {n["path"] for n in rows}
        require(len(paths) == len(rows) and "." in paths, "node paths " + sample["id"])
        for node in rows:
            path = node["path"]
            if path != ".":
                require((path.rpartition("/")[0] or ".") in paths, "missing parent " + path)
            for key in ("local", "world"):
                if key in node:
                    m = node[key]
                    require(len(m) == 16 and all(isinstance(v, (int,float)) and math.isfinite(v) for v in m), "bad transform")
                    require(m[3] == m[7] == m[11] == 0 and m[15] == 1, "matrix convention")
            if "mesh" in node and not node["mesh"].get("missing", False):
                mesh = node["mesh"]
                require(all(math.isfinite(v) and v >= 0 for v in mesh["bounds_local_m"]["size"]), "invalid mesh bounds")
                require(len(mesh["surfaces"]) > 0, "empty mesh")
                for surface in mesh["surfaces"]:
                    require(surface["vertices"] > 0 and surface["indices"] >= 0, "empty surface")
        require(sample["counts"]["nodes"] == len(rows), "node count")
        require(sample["counts"]["mesh_nodes"] == sum("mesh" in n and not n["mesh"].get("missing", False) for n in rows), "mesh count")
    require(by_id["map_briefing"]["context"]["shops"] == 3, "shop count")
    require(by_id["enemy_quaternius_experimental"]["counts"]["skeletons"] > 0, "experimental skeleton missing")
    print("ASSET_RUNTIME_REPORT_PASS", len(samples), "samples; visual approval not asserted")

if __name__ == "__main__":
    validate(json.loads(Path(sys.argv[1]).read_text(encoding="utf-8")))
