"""Run and verify real-map LOD QA locally; no CI or visual approval implied."""
import argparse
from collections import Counter
import json
import math
from pathlib import Path
import re
import shutil
import struct
import subprocess
import sys
import tempfile
import os

FAMILIES = {
    "barricade": (4, "structure", True, None),
    "container_corners": (4, "structure", True, (864, 216, 96)),
    "barrel": (8, "object", False, (3072, 576, 192)),
    "shop": (3, "object", False, (864, 216, 96)),
    "light_post": (4, "object", False, (1632, 360, 144)),
}
DISTANCES = (4, 12, 13.2, 30, 31.2, 30, 28.8, 12, 10.8)
LEVELS = (0, 0, 1, 1, 2, 2, 1, 1, 0)
CAPS = {"structure": ((20000, 8000, 2000), 8), "object": ((8000, 2800, 700), 4)}
ERROR = re.compile(r"SCRIPT ERROR:|Parse Error|WORLD_LOD_FAIL")


def require(ok, message):
    if not ok:
        raise ValueError(message)


def finite(value):
    return type(value) in (int, float) and math.isfinite(value)


def verify_report(report):
    assemblies, rows = report["assemblies"], report["checks"]
    require(report.get("hardware_validated") is False, "unexpected hardware approval")
    require(len(assemblies) == 23 and len(rows) == 207, "assembly/check count")
    require(Counter(a["family"] for a in assemblies) == Counter({k: v[0] for k, v in FAMILIES.items()}), "family coverage")
    require(len({a["path"] for a in assemblies}) == 23, "duplicate assembly path")
    totals = [0, 0, 0]
    pieces = 0
    for index, a in enumerate(assemblies):
        family = a["family"]
        _, category, blocking, exact = FAMILIES[family]
        cap, slots = CAPS[category]
        triangles = a["triangles_by_level"]
        policy = "existing_box" if blocking else "nonblocking"
        require(a["category"] == category and a["collision_policy"] == policy and a["colliders"] == int(blocking), f"collision policy {index}")
        require(a["collision_triangles"] == 0 and a["hardware_validated"] is False and a["limits_provisional"] is True, f"budget status {index}")
        require(len(triangles) == 3 and all(type(n) is int and 0 < n <= c for n, c in zip(triangles, cap)) and triangles[0] > triangles[1] > triangles[2], f"triangle budget {index}")
        require(tuple(triangles) == exact if exact else tuple(triangles) in ((3456,864,384),(2592,648,288)), f"triangle recipe {index}")
        expected_parts = {"container_corners":2,"barrel":4,"shop":2,"light_post":3}.get(family, triangles[0] // 432)
        require(a["material_slots"] == expected_parts and 0 < expected_parts <= slots, f"part/slot count {index}")
        pieces += expected_parts
        totals = [x+y for x,y in zip(totals,triangles)]
        checks = rows[index*9:(index+1)*9]
        baseline = checks[0]["hit_z"]
        size = checks[0]["collider_size"]
        require(len(size)==3 and all(finite(n) for n in size), f"collider dimensions {index}")
        require(all(n>0 for n in size) and finite(baseline) if blocking else size==[0,0,0] and baseline is None, f"baseline ray {index}")
        for row, distance, level in zip(checks,DISTANCES,LEVELS):
            require(row["assembly"] == index and row["family"] == family and row["category"] == category, f"row identity {index}")
            require(finite(row["distance_m"]) and abs(row["distance_m"]-distance)<1e-5 and row["level"]==level and row["triangles"]==triangles[level], f"LOD sequence {index}")
            require(row["collision_policy"]==policy and row["shape_id_unchanged"] is True and row["collider_size"]==size, f"collider invariant {index}")
            hit=row["hit_z"]
            require(finite(hit) and abs(hit-baseline)<=0.002 if blocking else hit is None, f"ray invariant {index}")
    require(pieces==86 and totals==[49248,10584,4128], "aggregate geometry")
    return {"assemblies":23,"checks":207,"pieces":pieces,"triangles_by_level":totals,"blockers":8,"nonblocking":15,"hardware_validated":False,"visual_reviewed":False}


def verify_directory(directory):
    report = json.loads((directory / "world-lod-report.json").read_text(encoding="utf-8"))
    summary = verify_report(report)
    for family in FAMILIES:
        for suffix in ("lod", "fixed-lod"):
            for level in range(3):
                path=directory / f"{family}-{suffix}{level}.png"
                with path.open("rb") as file:
                    header=file.read(24)
                require(len(header)==24 and header[:16]==b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR" and struct.unpack(">II",header[16:])==(1280,720) and path.stat().st_size>33, f"missing/invalid PNG header: {path.name}")
    summary["capture_headers_checked"]=30
    return summary


def git(root,*args):
    return subprocess.check_output(["git","-C",str(root),*args],text=True).strip()


def run_local(root, output, godot):
    require(not output.exists(), "use a new output directory")
    require(not output.is_relative_to(root), "output must be outside repository")
    require(not git(root,"status","--porcelain"), "start with a clean checkout")
    commit=git(root,"rev-parse","HEAD")
    output.mkdir(parents=True)
    env=os.environ.copy()
    env["FRONTLINE_LOD_DIR"]=str(output)
    # Isolate the normal user:// directory from the player profile.
    profile=output/"profile"
    profile.mkdir()
    env["XDG_DATA_HOME"]=str(profile)
    if os.name=="nt":
        env["APPDATA"]=str(profile)
        env["LOCALAPPDATA"]=str(profile)
    elif sys.platform=="darwin":
        raise ValueError("local runner currently supports Windows and Linux only")
    def run(name,args,timeout,marker=None,*,cwd=root):
        try:
            result=subprocess.run(args,cwd=cwd,env=env,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,timeout=timeout)
        except subprocess.TimeoutExpired as exc:
            (output / (name+".log")).write_bytes(exc.stdout or b"")
            raise
        data=result.stdout.decode("utf-8",errors="replace")
        (output / (name+".log")).write_text(data,encoding="utf-8")
        require(result.returncode==0 and not ERROR.search(data) and (marker is None or marker in data),f"{name} failed; inspect log")
    run("version",[godot,"--version"],15,"4.4.1")
    run("budget",[sys.executable,"-m","unittest","discover","-s","tests","-p","test_world_lod_contract.py","-v"],120)
    # Godot writes import metadata and UIDs beside resources, including tracked
    # files. Import a snapshot so QA never changes the source checkout.
    with tempfile.TemporaryDirectory(prefix="frontline-lod-") as temporary:
        staging = Path(temporary)
        archive = staging / "project.zip"
        project = staging / "project"
        subprocess.run(
            ["git", "-C", str(root), "archive", "--format=zip", "-o", str(archive), commit],
            check=True,
            timeout=120,
        )
        shutil.unpack_archive(archive, project)
        run("import", [godot, "--headless", "--editor", "--import", "--path", str(project)],
            180, cwd=project)
        run("godot", [godot, "--path", str(project), "--rendering-driver", "opengl3",
                      "--script", "res://tools/asset_pipeline/runtime/world_lod_qa.gd"],
            240, "WORLD_LOD_PASS 207", cwd=project)
    require(git(root,"rev-parse","HEAD")==commit and not git(root,"status","--porcelain"),"checkout changed during run")
    summary=verify_directory(output)
    summary["commit"]=commit
    summary["provenance"]="local_runner_clean_checkout"
    (output/"local-summary.json").write_text(json.dumps(summary,indent=2)+"\n",encoding="utf-8")
    return summary


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output",type=Path)
    parser.add_argument("--godot",default="godot")
    parser.add_argument("--verify-only",action="store_true")
    args=parser.parse_args()
    directory=args.output.resolve()
    try:
        summary=verify_directory(directory) if args.verify_only else run_local(Path(__file__).resolve().parents[2],directory,args.godot)
    except (ValueError,KeyError,IndexError,TypeError,OSError,subprocess.SubprocessError) as exc:
        print(f"WORLD_LOD_LOCAL_FAIL: {exc}",file=sys.stderr)
        return 1
    print(json.dumps(summary,indent=2))
    return 0

if __name__=="__main__":
    raise SystemExit(main())
