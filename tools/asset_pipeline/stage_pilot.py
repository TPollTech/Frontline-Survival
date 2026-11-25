"""Stage generated QA export bytes into a separate Studio package, never production Pages."""
import argparse,json,shutil
from pathlib import Path
from tools.asset_pipeline.live_catalog import canonical
from tools.asset_pipeline.validate_gltf import digest

def main():
    p=argparse.ArgumentParser();p.add_argument("pilot");p.add_argument("studio");a=p.parse_args()
    source,stage=Path(a.pilot),Path(a.studio)
    catalog=json.loads((stage/"live_catalog.json").read_text())
    report=json.loads((source/"pilot-report.json").read_text())
    if catalog["revision"]!=report["revision"]:raise ValueError("revision mismatch")
    if any(x["id"]==report["id"] for x in catalog["assets"]):raise ValueError("duplicate pilot")
    slug=report.get("slug","industrial-bollard")
    if not slug or not all(c.isalnum() or c in "-_" for c in slug):raise ValueError("invalid pilot slug")
    category=report["category"]
    outputs=[]
    for row in report["exports"]:
        if row["path"]!="asset.glb":continue
        name=f'lod{row["level"]}/asset.glb';target="qa-pilots/"+slug+"/"+name
        f=stage/target;f.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(source/name,f)
        if digest(f.read_bytes())!=row["sha256"]:raise ValueError("pilot bytes differ")
        catalog["resources"][target]={"sha256":row["sha256"],"bytes":f.stat().st_size,"status":"new","category":category,"gltf_dependencies":[]}
        outputs.append({"path":target,"role":"lod"+str(row["level"])})
    catalog["assets"].append({"id":report["id"],"category":category,"usage":"QA_ONLY — not integrated into production gameplay",
        "source":{"path":report["source"],"editable":True},"outputs":outputs,
        "preview":{"resource":outputs[0]["path"],"mode":"glb","fidelity":"exact_generated_bytes"},
        "collision":report["collision"],"lods":{"distances_m":report["lod_distances_m"],"levels":[{"path":o["path"],"role":o["role"]} for o in outputs]},
        "dependencies":{"resources":[],"assets":[],"sources":[report["source"]]},
        "runtime_samples":[],"validation":{"approved":False,"runtime":"qa_only","studio_visual":"pending","godot_visual":"pending"},
        "gaps":["QA-only pilot; no manual visual approval or production integration."]})
    (stage/"live_catalog.json").write_bytes(canonical(catalog))
    print("PILOT_STAGE_PASS",len(outputs))
if __name__=="__main__":main()
