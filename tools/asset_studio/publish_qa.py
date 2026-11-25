"""Create a separate, QA-only Studio with actual model bytes and Godot evidence."""
import argparse,json,hashlib,shutil,struct,subprocess,sys
from pathlib import Path
from tools.asset_pipeline.live_catalog import canonical
from tools.asset_pipeline.parametric.lod import BUDGETS,NON_GEOMETRY_CATEGORIES
from tools.asset_studio.native_evidence import stage_native

def require(value,message):
    if not value:raise ValueError(message)

def main():
    p=argparse.ArgumentParser();p.add_argument("production");p.add_argument("suite");p.add_argument("bollard");p.add_argument("inventory");args=p.parse_args()
    prod,suite,bollard=map(Path,(args.production,args.suite,args.bollard))
    catalog=json.loads((prod/"live_catalog.json").read_text());qa=prod/"qa";qa.mkdir()
    for name in ("index.html","studio.css","studio.js","lighting.js","camera-navigation.js","inspection.js","serve_offline.py","studio-light.hdr","studio-light.json"):
        shutil.copyfile(prod/name,qa/name)
    shutil.copytree(prod/"vendor",qa/"vendor")
    q={"kind":catalog["kind"],"schema_version":catalog["schema_version"],"revision":catalog["revision"],"assets":[],"resources":{},"runtime_samples":{},"approved":False,"scope":"QA_ONLY"}
    target=qa/"live_catalog.json";target.write_bytes(canonical(q))
    names=json.loads((suite/"suite.json").read_text())["pilots"]
    folders=[bollard]+[suite/n for n in names]
    for folder in folders:
        subprocess.run([sys.executable,"-m","tools.asset_pipeline.stage_pilot",str(folder),str(qa)],check=True)
    q=json.loads(target.read_text())
    byid={a["id"]:a for a in q["assets"]};total=0;posed_total=0
    for folder in folders:
        report=json.loads((folder/"pilot-report.json").read_text())
        engine=json.loads((folder/"godot-report.json").read_text())
        require(report["revision"]==engine["revision"]==q["revision"] and not engine["visual_approval"],"revision or approval mismatch")
        a=byid[report["id"]];slug=report.get("slug","industrial-bollard")
        a["runtime_views"]=[]
        for row in engine["rows"]:
            level=row["level"];expected=next(x for x in report["exports"] if x["level"]==level and x["path"]=="asset.glb")
            require(row["sha256"]==expected["sha256"] and row["triangles"]==expected["metrics"]["triangles"],"engine export mismatch")
            name=f"qa-pilots/{slug}/godot-lod{level}.png"
            data=(folder/f"godot-lod{level}.png").read_bytes()
            require(len(data)>1000 and data[:8]==b"\x89PNG\r\n\x1a\n" and data[12:16]==b"IHDR","invalid capture")
            w,h=struct.unpack(">II",data[16:24]);require(w>=640 and h>=360,"capture size")
            (qa/name).write_bytes(data)
            a["runtime_views"].append({"id":"godot-lod"+str(level),"label":"Godot QA — LOD "+str(level),"resource":name,"sha256":hashlib.sha256(data).hexdigest(),"width":w,"height":h,"fidelity":"actual_godot_frame","camera":{"path":row["camera"]},"context":{"kind":"qa_native_camera_placement","model_sha256":row["sha256"],"triangles":row["triangles"]},"approved":False})
            total+=1
            if expected.get("rig"):
                rig=row.get("rig",{})
                require(rig.get("child_displacement_m",0)>.001,"rig pose missing")
                posed=(folder/f"godot-pose-lod{level}.png").read_bytes()
                require(len(posed)>1000 and posed[:8]==b"\x89PNG\r\n\x1a\n" and posed[12:16]==b"IHDR","invalid posed capture")
                pw,ph=struct.unpack(">II",posed[16:24]);require((pw,ph)==(w,h),"posed resolution mismatch")
                pose_name=f"qa-pilots/{slug}/godot-pose-lod{level}.png"
                (qa/pose_name).write_bytes(posed)
                a["runtime_views"].append({"id":"godot-pose-lod"+str(level),"label":"Godot QA — pose LOD "+str(level),"resource":pose_name,"sha256":hashlib.sha256(posed).hexdigest(),"width":pw,"height":ph,"fidelity":"actual_godot_frame","camera":{"path":row["camera"]},"context":{"kind":"qa_skeleton_pose","model_sha256":row["sha256"],"pose":rig},"approved":False})
                posed_total+=1
    q["runtime_views"]={"revision":q["revision"],"count":total,"posed_count":posed_total,"approved":False}
    q["assets"].sort(key=lambda a:a["id"])
    target.write_bytes(canonical(q))
    covered={a["category"] for a in q["assets"]}
    require(covered==set(BUDGETS),"geometric pilot coverage incomplete: "+str(set(BUDGETS)-covered))
    require(total==len(folders)*3,"capture coverage mismatch")
    require(posed_total==6,"pose capture coverage mismatch")
    categories=sorted(set(BUDGETS)|set(NON_GEOMETRY_CATEGORIES)|{a["category"] for a in catalog["assets"]})
    coverage=[{"category":c,"pilots":[a["id"] for a in q["assets"] if a["category"]==c],"legacy":[a["id"] for a in catalog["assets"] if a["category"]==c],"status":"geometric_qa" if c in covered else "native_evidence_pending","approved":False} for c in categories]
    stage_native(prod,qa,catalog,args.inventory,coverage)
    (qa/"coverage.json").write_bytes(canonical({"revision":q["revision"],"categories":coverage,"approved":False}))
    page=qa/"index.html"
    page.write_text(page.read_text().replace("ASSET STUDIO / INSPEÇÃO TÉCNICA","ASSET STUDIO / QA — NÃO HOMOLOGADO").replace('<div id="revision">','<a href="../" style="color:inherit">Voltar ao Studio de produção</a><div id="revision">').replace('<h1>Biblioteca</h1>','<h1>Pilotos QA</h1><p class="muted">Modelos experimentais, não integrados à produção. <a href="coverage.html">Cobertura por categoria</a>.</p>'),encoding="utf-8")
    page=prod/"index.html"
    page.write_text(page.read_text().replace('<div id="revision">','<a href="qa/" style="color:inherit">Pilotos QA · não homologados</a><div id="revision">'),encoding="utf-8")
    print("QA_SECTION_STAGE_PASS",len(q["assets"]),total,len(covered),flush=True)
if __name__=="__main__":main()
