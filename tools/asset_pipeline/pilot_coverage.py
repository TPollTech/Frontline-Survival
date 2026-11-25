"""Track pilot coverage without promoting legacy observations into visual approvals."""
import argparse,json
from pathlib import Path
from tools.asset_pipeline.live_catalog import canonical
from tools.asset_pipeline.parametric.lod import BUDGETS

def coverage(catalog):
    groups={}
    for a in catalog["assets"]:
        c=a["category"]
        group=groups.setdefault(c,{"category":c,"assets":[],"sampled":[],"files":[]})
        group["assets"].append(a["id"])
        if a.get("runtime_samples"):group["sampled"].append(a["id"])
        for o in a.get("outputs",[]):
            path=o["path"]
            if Path(path).suffix.lower() in (".glb",".gltf") and catalog["resources"].get(path,{}).get("status")!="missing":
                group["files"].append(path)
    rows=[]
    for c in sorted(set(groups)|set(BUDGETS)):
        row=groups.get(c,{"category":c,"assets":[],"sampled":[],"files":[]})
        for k in ("assets","sampled","files"):row[k]=sorted(set(row[k]))
        row["candidate"]=next(iter(row["sampled"] or row["assets"]),None)
        row["state"]="legacy_evidence" if row["sampled"] else "candidate_unverified" if row["assets"] else "no_existing_category"
        row["canonical_pilot"]="qa:industrial_bollard" if c=="object" else None
        row["approved"]=False
        rows.append(row)
    return {"revision":catalog["revision"],"categories":rows,"visual_approval":False}
def main():
    p=argparse.ArgumentParser();p.add_argument("catalog");p.add_argument("output");a=p.parse_args()
    r=coverage(json.loads(Path(a.catalog).read_text()));Path(a.output).write_bytes(canonical(r))
    print("PILOT_COVERAGE_PASS",len(r["categories"]))
if __name__=="__main__":main()
