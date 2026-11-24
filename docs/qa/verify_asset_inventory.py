"""Verify the immutable baseline inventory from a Git checkout (stdlib only).

This checks evidence and coverage, not visual geometry or live runtime instances.
Run from any directory: python docs/qa/verify_asset_inventory.py
"""
import json
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "docs" / "asset_inventory_baseline.json"


def git(*args):
    return subprocess.check_output(["git", "-C", str(ROOT), *args])


def require(condition, message):
    if not condition:
        raise ValueError(message)


def main():
    data = json.loads(DATA.read_text(encoding="utf-8"))
    baseline = data["baseline_commit"]
    require(git("rev-parse", baseline + "^{tree}").decode().strip() ==
            data["baseline_tree"], "baseline tree differs")
    tree = {}
    for item in git("ls-tree", "-r", "-l", "-z", baseline).split(b"\0"):
        if not item:
            continue
        meta, name = item.split(b"\t", 1)
        _, kind, sha, size = meta.decode().split()
        if kind == "blob":
            tree[name.decode("utf-8")] = (sha, int(size))
    files = data["files"]
    require(len({x["path"] for x in files}) == len(files), "duplicate asset")
    require({x["path"] for x in files} ==
            {p for p in tree if p.startswith("assets/")}, "asset coverage differs")
    for entry in files + data["source_scripts"] + data["scenes"] + data["tooling"] + data["qa_resources"]:
        path = entry["path"]
        require(path in tree and tree[path][0] == entry["git_blob_sha1"],
                "blob differs: " + path)
        if "bytes" in entry:
            require(tree[path][1] == entry["bytes"], "size differs: " + path)
    require({x["path"] for x in data["source_scripts"]} ==
            {p for p in tree if p.startswith("scripts/")}, "script coverage differs")
    require({x["path"] for x in data["scenes"]} ==
            {p for p in tree if p.startswith("scenes/") and p.endswith(".tscn")},
            "scene coverage differs")
    source_cache = {}

    def source_line(path, line):
        if path not in source_cache:
            source_cache[path] = git("show", baseline + ":" + path).decode("utf-8").splitlines()
        require(1 <= line <= len(source_cache[path]), "source line missing: " + path)
        return source_cache[path][line - 1].strip()

    for ref in data["references"]:
        require("res://" + ref["target"] in source_line(ref["source"], ref["line"]),
                "reference anchor differs: " + ref["source"])
        if ref["kind"] == "literal":
            require(ref["target"] in tree, "missing literal: " + ref["target"])
    for expansion in data["dynamic_expansions"]:
        require(all(p in tree for p in expansion["present"]), "dynamic present mismatch")
        require(all(p not in tree for p in expansion["absent"]), "dynamic absent mismatch")
    for entry in files:
        if entry["category"] == "import_metadata":
            require(entry["source"] in tree, "orphan import")
    families = data["runtime_families"]
    require(len({f["id"] for f in families}) == len(families), "duplicate family")
    require(all(f["source"] in tree for f in families), "missing family source")
    covered = {(f["source"], line) for f in families for line in f["site_lines"]}
    for site in data["constructor_sites"]:
        require((site["source"], site["line"]) in covered, "unmapped site")
        require(source_line(site["source"], site["line"]) == site["expression"],
                "constructor anchor differs: " + site["source"])
    require(not data["unclassified_constructor_sites"], "unclassified sites remain")
    require(all(f["runtime_capture"] == "pending" for f in families),
            "baseline must not claim runtime capture")
    print(f"ASSET_INVENTORY_STATIC_PASS: {len(files)} files, {len(families)} runtime families")
    print("Runtime/visual validation still pending.")


if __name__ == "__main__":
    main()
