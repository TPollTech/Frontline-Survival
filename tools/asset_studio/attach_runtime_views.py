"""Attach authentic render captures to the staged catalog. Never synthesize previews."""
import argparse, hashlib, json, struct, shutil
from pathlib import Path

EXPECTED={"fps":("viewmodel:assembly","Primeira pessoa — câmera real"),
          "map_top":("map:campo_de_testes","Mapa completo — superior"),
          "map_overview":("map:campo_de_testes","Mapa completo — perspectiva"),
          "external_character":("ally:legacy","Personagem — câmera externa de inspeção")}

def require(ok,message):
    if not ok: raise ValueError(message)

def attach(stage,capture):
    stage,capture=Path(stage),Path(capture)
    catpath=stage/"live_catalog.json"
    cat=json.loads(catpath.read_text(encoding="utf-8"))
    report=json.loads((capture/"views.json").read_text(encoding="utf-8"))
    require(report.get("kind")=="frontline_godot_views" and report.get("schema_version")==1 and report.get("revision")==cat["revision"],"capture revision mismatch")
    require(report.get("display") not in (None,"","headless") and report.get("approved") is False,"invalid render evidence")
    rows=report["views"]
    require(len(rows)==len(EXPECTED) and {r["id"] for r in rows}==set(EXPECTED),"incomplete capture set")
    byid={a["id"]:a for a in cat["assets"]}
    out=stage/"runtime-views"
    require(not out.exists(),"capture already attached")
    records=[]
    for r in rows:
        id=r["id"]
        asset,label=EXPECTED[id]
        require(r["asset_id"]==asset and asset in byid and r["file"]==id+".png","invalid capture mapping")
        data=(capture/r["file"]).read_bytes()
        require(len(data)>1000 and data[:8]==b"\x89PNG\r\n\x1a\n" and data[12:16]==b"IHDR","invalid PNG")
        w,h=struct.unpack(">II",data[16:24])
        require((w,h)==(r["width"],r["height"]) and w>=640 and h>=360,"PNG size mismatch")
        require(len(r["camera"]["world_basis_origin"])==4 and r["camera"]["path"],"missing camera evidence")
        context=r["context"]
        if id.startswith("map_"):
            require(context["visible_mesh_nodes"]>=30 and context["shops"]==3 and all(b>a for a,b in zip(context["bounds_min_m"],context["bounds_max_m"])),"incomplete map")
        if id=="external_character":
            require(context["native_player_tps"] is False and context["visible_mesh_nodes"]>0,"incorrect third person claim")
        records.append({**r,"label":label,"resource":"runtime-views/"+r["file"],"sha256":hashlib.sha256(data).hexdigest(),"bytes":len(data),"fidelity":"actual_godot_frame","approved":False})
    out.mkdir()
    for r in records:
        shutil.copyfile(capture/r["file"],stage/r["resource"])
        byid[r["asset_id"]].setdefault("runtime_views",[]).append(r)
    cat["runtime_views"]={"kind":report["kind"],"revision":report["revision"],"engine":report["engine"],"scene":report["scene"],"display":report["display"],"count":len(records),"approved":False}
    catpath.write_text(json.dumps(cat,ensure_ascii=False,sort_keys=True,indent=2)+"\n",encoding="utf-8")
    print("RUNTIME_VIEWS_STAGE_PASS",len(records))

if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("stage");parser.add_argument("capture")
    args=parser.parse_args()
    attach(args.stage,args.capture)
