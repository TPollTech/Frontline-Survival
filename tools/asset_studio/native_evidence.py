"""Expose actual native observations; never substitute a geometry for nongeometry."""
import hashlib,html,json,shutil
from pathlib import Path
from tools.asset_pipeline.live_catalog import canonical

def native_evidence(catalog,inventory):
    if inventory["commit"]!=catalog["revision"] or inventory["failures"]:
        raise ValueError("native evidence revision or failures")
    samples=inventory["samples"]
    physical=inventory["physical_resources"]
    result={}
    for category,key in (("audio","length_s"),("texture","dimensions_px")):
        candidates=[r for r in physical if r.get("loaded") and r.get(key) and r["path"] in catalog["resources"] and catalog["resources"][r["path"]].get("sha256")]
        candidates.sort(key=lambda r:r["path"])
        result[category]={"observations":candidates[:3],"kind":"actual_imported_resource","scope":"loaded native resource; no new authored source"}
    for category,key in (("camera","camera"),("shader","canvas_material")):
        rows=[]
        for s in samples:
            for n in s["nodes"]:
                v=n.get(key)
                if not isinstance(v,dict):continue
                if category=="shader" and not v.get("shader"):continue
                rows.append({"sample":s["id"],"families":s["families"],"node":n.get("path"),"data":v})
                if len(rows)>=3:break
            if len(rows)>=3:break
        result[category]={"observations":rows,"kind":"actual_runtime_node","scope":"sampled native node; not visual or semantic approval"}
    result["material"]={"observations":[{"name":k,"data":v} for k,v in sorted(inventory["library_materials"].items())],"kind":"actual_engine_library","scope":"material library values; not proof of effective assignment"}
    result["physics_query"]={"observations":[r for r in inventory["query_records"] if r.get("executed")],"kind":"actual_query_results","scope":"executed game methods; query shape metadata may be source-reviewed"}
    for row in result.values():row["approved"]=False
    return result

def stage_native(prod,qa,catalog,inventory_path,coverage):
    inventory=json.loads(Path(inventory_path).read_text())
    records=native_evidence(catalog,inventory)
    esc=lambda x:html.escape(str(x),quote=True)
    blocks=[]
    for row in coverage:
        c=row["category"];record=records.get(c)
        if record and record["observations"]:row["status"]="native_sample_evidence";row["native_observations"]=len(record["observations"])
        previews=[]
        if c in ("audio","texture") and record:
            for item in record["observations"]:
                path=item["path"];meta=catalog["resources"][path];source=prod/path
                data=source.read_bytes()
                if hashlib.sha256(data).hexdigest()!=meta["sha256"]:raise ValueError("resource hash mismatch")
                target=qa/"native"/path;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(data)
                item["sha256"]=meta["sha256"];item["preview_path"]="native/"+path
                uri=esc(item["preview_path"])
                tag=f'<audio controls preload="none" src="{uri}"></audio>' if c=="audio" else f'<img loading="lazy" src="{uri}" alt="{esc(path)}" width="160">'
                previews.append(f'<div><p>{esc(path)}</p>{tag}</div>')
        evidence=f'<details><summary>Evidência nativa ({len(record["observations"])} registros)</summary><p>{esc(record["scope"])}</p>{"".join(previews)}<pre>{esc(json.dumps(record["observations"],ensure_ascii=False,indent=2))}</pre></details>' if record else ""
        blocks.append(f'<section><h2>{esc(c)}</h2><p>{esc(row["status"])} · Pilotos: {esc(", ".join(row["pilots"]) or "nenhum")}</p><p>Legado: {esc(", ".join(row["legacy"]) or "nenhum")}</p>{evidence}</section>')
    (qa/"native-evidence.json").write_bytes(canonical({"revision":catalog["revision"],"categories":records,"approved":False}))
    (qa/"coverage.html").write_text('<!doctype html><html lang="pt-BR"><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>Cobertura QA</title><style>body{background:#10151b;color:#dce5ed;font:15px/1.5 system-ui;max-width:960px;margin:auto;padding:24px}a{color:#7fd5ee}section{border-top:1px solid #354352;padding:12px 0}h2{font-size:18px}pre{white-space:pre-wrap;overflow-wrap:anywhere;font-size:12px}audio{max-width:100%}img{max-width:100%;height:auto}</style><a href="./">Voltar aos pilotos</a><h1>Cobertura técnica de QA</h1><p>Não homologado. Amostras nativas não equivalem a novos assets canônicos ou validação visual.</p><p>Revisão '+esc(catalog["revision"])+'</p>'+''.join(blocks)+'</html>',encoding="utf-8")
    print("NATIVE_EVIDENCE_PASS",json.dumps({k:len(v["observations"]) for k,v in records.items()},sort_keys=True),flush=True)
