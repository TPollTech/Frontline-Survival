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
    # Reconcile the real capture against the immutable canonical manifest.
    manifest = json.loads((Path(__file__).resolve().parents[2] / "assets/catalog/manifest.json").read_text(encoding="utf-8"))
    registered = manifest["resources"]
    physical = {r["path"]: r for r in data["physical_resources"]}
    require(len(physical) == len(data["physical_resources"]) == len(registered) and set(physical) == set(registered), "physical coverage")
    for path, record in physical.items():
        require(record["category"] == registered[path]["category"], "resource kind")
        if record["category"] == "import_metadata":
            require(record["file_exists"], "metadata missing")
        else:
            require(record["loaded"], "resource load failed: " + path)
            if record["category"] == "audio":
                require(record.get("length_s", 0) > 0, "empty audio: " + path)
            if record["category"] == "texture":
                require(all(v > 0 for v in record["dimensions_px"]), "empty texture")
    queries = {r["family"]: r for r in data["query_records"]}
    require(set(queries) == {"query:spawn", "query:enemy_tactics", "query:turret"}, "query coverage")
    require(all(r["executed"] and r["shape_origin"] == "source_review" for r in queries.values()), "query evidence")
    require(queries["query:spawn"]["result_valid"], "spawn failed")
    for key in ("enemy_tracer", "airstrike_marker", "airstrike_impact"):
        require(key in by_id and by_id[key]["counts"]["mesh_nodes"] > 0, "missing effect " + key)
    families = {f for s in samples for f in s["families"]} | set(queries)
    expected = {a["id"] for a in manifest["assets"] if a["source"]["kind"] == "godot_recipe"}
    require(families == expected, "family sample coverage differs")
    mesh_paths = set()
    effective_textures = set()
    audio_paths = set()
    tangents_missing = 0
    for sample in samples:
        for node in sample["nodes"]:
            if "audio" in node and node["audio"]["path"].startswith("res://"):
                audio_paths.add(node["audio"]["path"][6:])
            mesh = node.get("mesh")
            if not mesh or mesh.get("missing"):
                continue
            path = mesh["path"].split("::", 1)[0]
            if path.startswith("res://") and path.endswith(".glb"):
                mesh_paths.add(path[6:])
            for surface in mesh["surfaces"]:
                require(isinstance(surface.get("tangents"), int) and surface["tangents"] >= 0, "missing tangent metric")
                tangents_missing += int(surface["tangents"] == 0)
                for k, v in (surface.get("effective_material") or {}).items():
                    if k.endswith("_texture") and isinstance(v, dict) and v["path"].startswith("res://"):
                        effective_textures.add(v["path"][6:])
    expected_glbs = {p for p in registered if p.endswith(".glb")}
    require(mesh_paths == expected_glbs, "GLB coverage")
    library_textures = {v["path"][6:] for m in data["library_materials"].values() for k, v in m.items()
                        if k.endswith("_texture") and isinstance(v, dict) and v["path"].startswith("res://")}
    require(library_textures == {p for p in registered if p.startswith("assets/textures/weapon_")}, "library texture coverage")
    summary = {"samples": len(samples), "physical_resources": len(physical), "glb_observed": len(mesh_paths),
               "families_tagged_or_queries_executed": len(families), "effective_textures": sorted(effective_textures),
               "library_textures": sorted(library_textures), "audio_paths_in_nodes": sorted(audio_paths),
               "surface_records_without_tangents": tangents_missing, "queries": list(queries.values()),
               "limitations": data["limitations"], "approved": False}
    print("ASSET_RUNTIME_RECONCILIATION " + json.dumps(summary, sort_keys=True))
    if len(sys.argv) > 2:
        Path(sys.argv[2]).write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print("ASSET_RUNTIME_REPORT_PASS", len(samples), "samples; visual approval not asserted")

if __name__ == "__main__":
    validate(json.loads(Path(sys.argv[1]).read_text(encoding="utf-8")))
