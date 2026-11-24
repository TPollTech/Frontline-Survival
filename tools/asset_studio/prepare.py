"""Stage local Studio with verified original resources; never edit game files."""
import argparse,sys,shutil,json
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[2]))
from tools.asset_pipeline.live_catalog import build,canonical,safe,fingerprint
def main():
    p=argparse.ArgumentParser()
    p.add_argument("output")
    p.add_argument("--runtime")
    args=p.parse_args()
    root=Path(__file__).resolve().parents[2]
    out=Path(args.output).resolve()
    if out==root or out.is_relative_to(root):
        raise ValueError("stage outside repository")
    out.mkdir(parents=True,exist_ok=True)
    if any(out.iterdir()):raise ValueError("stage must be empty")
    runtime=json.loads(Path(args.runtime).read_text()) if args.runtime else None
    catalog=build(root,runtime=runtime)
    for name,rec in catalog["resources"].items():
        if rec["status"]=="missing":continue
        src=safe(root,name)
        dst=safe(out,name)
        dst.parent.mkdir(parents=True,exist_ok=True)
        shutil.copyfile(src,dst)
        if fingerprint(out,name)["sha256"]!=rec["sha256"]:raise ValueError("copy mismatch "+name)
    studio=root/"tools/asset_studio"
    for name in ("index.html","studio.css","studio.js","lighting.js"):shutil.copyfile(studio/name,out/name)
    from generate_hdri import write
    write(out)
    three=studio/"node_modules/three"
    for name in ("build","examples/jsm"):
        shutil.copytree(three/name,out/"vendor/three"/name)
    shutil.copyfile(three/"LICENSE",out/"vendor/three/LICENSE")
    (out/"live_catalog.json").write_bytes(canonical(catalog))
    print("STUDIO_STAGE_PASS",json.dumps(catalog["counts"],sort_keys=True))
if __name__=="__main__":main()
