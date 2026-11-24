"""Join the static and Godot evidence by revision, original path and hash."""
import argparse,json
from collections import Counter
from pathlib import Path
from tools.asset_pipeline.live_catalog import canonical

def reconcile(static,engine):
    if static["revision"]!=engine["revision"]:raise ValueError("revision mismatch")
    def indexed(rows):
        out={r["path"]:r for r in rows}
        if len(out)!=len(rows):raise ValueError("duplicate path")
        return out
    a,b=indexed(static["files"]),indexed(engine["files"])
    if set(a)!=set(b):raise ValueError("import coverage mismatch")
    rows=[]
    for p in sorted(a):
        x,y=a[p],b[p];m=x["metrics"];problems=[]
        if x["sha256"]!=y["sha256"]:problems.append("source hash mismatch")
        if x["errors"]:problems.append("static hard errors")
        if y["import_code"]!=0 or not y["mesh_nodes"]:problems.append("Godot import failure")
        known=m.get("triangles") is not None and not m.get("unknown_topology") and not y["unknown_topology"]
        if known and m["triangles"]!=y["triangles"]:problems.append("triangle count mismatch")
        rows.append({"path":p,"sha256":x["sha256"],"static_triangles":m.get("triangles"),"godot_triangles":y["triangles"],"triangle_comparison":"match" if known and m["triangles"]==y["triangles"] else "mismatch" if known else "unknown","problems":problems,"warnings":x["warnings"],"unknown":x["unknown"],"visual_approval":False})
    return {"revision":static["revision"],"rows":rows,"hard_failures":sum(bool(x["problems"]) for x in rows)+len(static["missing_catalog_references"]),"comparisons":dict(Counter(x["triangle_comparison"] for x in rows)),"warning_codes":dict(Counter(w["code"] for x in rows for w in x["warnings"])),"visual_approval":False}
def main():
    p=argparse.ArgumentParser();p.add_argument("static");p.add_argument("engine");p.add_argument("output");a=p.parse_args()
    r=reconcile(json.loads(Path(a.static).read_text()),json.loads(Path(a.engine).read_text()))
    Path(a.output).write_bytes(canonical(r));print("VALIDATION_RECONCILED",json.dumps({k:r[k] for k in ("hard_failures","comparisons","warning_codes")},sort_keys=True))
    return 1 if r["hard_failures"] else 0
if __name__=="__main__":raise SystemExit(main())
