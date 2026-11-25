"""Live discovery, without altering the immutable historical manifest."""
import argparse
import copy
import hashlib
import json
from pathlib import Path
import re
import subprocess
import struct
import posixpath
from urllib.parse import unquote, urlsplit
from collections import Counter, defaultdict
try:
    from .runtime_catalog_evidence import dynamic_evidence, geometry_evidence
except ImportError:
    from runtime_catalog_evidence import dynamic_evidence, geometry_evidence

EXT={
 ".glb":"model",".gltf":"model",".obj":"model",".fbx":"model",".dae":"model",
 ".blend":"model_source",".tscn":"scene",".scn":"scene",".tres":"resource",".res":"resource",
 ".png":"texture",".jpg":"texture",".jpeg":"texture",".webp":"texture",".dds":"texture",
 ".ktx2":"texture",".hdr":"texture",".exr":"texture",".svg":"texture",
 ".wav":"audio",".ogg":"audio",".mp3":"audio",".gdshader":"shader",
 ".gdshaderinc":"shader",".import":"import_metadata",".bin":"buffer",
 ".anim":"animation",".material":"material"
}
REF=re.compile(r'res://([^"\'\s<>]+)')
DYNAMIC=re.compile(r'(?:%[sd]|%0\d+d|\{[^}]+\})')
PROCEDURAL=re.compile(r'\b(?:ArrayMesh|SurfaceTool|ImmediateMesh|(?:Box|Sphere|Capsule|Cylinder|Plane|Quad|Torus|Prism)Mesh|(?:Box|Sphere|Capsule|Cylinder|ConvexPolygon|ConcavePolygon)Shape3D|MeshInstance3D|Skeleton3D)\s*\.new\s*\(')
def require(ok,msg):
    if not ok: raise ValueError(msg)

def canonical(obj):
    return (json.dumps(obj,ensure_ascii=False,sort_keys=True,indent=2,allow_nan=False)+"\n").encode()

def sha(data):
    return hashlib.sha256(data).hexdigest()

def git(root,*args):
    return subprocess.check_output(["git","-C",str(root),*args])

def discover_paths(root):
    # Tracked plus nonignored working files; no .godot/cache, QA fixture outputs,
    # docs or previews mistaken for production. Literal external references
    # from project scripts/scenes may expand the set.
    raw=git(root,"ls-files","-z","--cached","--others","--exclude-standard")
    return sorted(set(x.decode("utf-8") for x in raw.split(b"\0") if x))

def safe(root,p):
    require(isinstance(p,str) and p and "\\" not in p and not p.startswith("/") and ":" not in p and all(x not in ("",".","..") for x in p.split("/")),"unsafe path: "+str(p))
    f=root.joinpath(*p.split("/"))
    require(f.resolve().is_relative_to(root) and not any(root.joinpath(*p.split("/")[:i]).is_symlink() for i in range(1,len(p.split("/"))+1)),"symlink path: "+p)
    return f

def fingerprint(root,p):
    f=safe(root,p)
    require(f.is_file(),"missing file: "+p)
    b=f.read_bytes()
    return {"bytes":len(b),"sha256":sha(b),"git_blob_sha1":hashlib.sha1(b"blob "+str(len(b)).encode()+b"\0"+b).hexdigest()}

def resolve_gltf_uri(source, uri):
    """Resolve a local glTF URI inside the repository, preserving its original spelling."""
    if not isinstance(uri, str) or not uri or any(ord(c) < 32 for c in uri):
        raise ValueError("invalid glTF URI")
    parsed = urlsplit(uri)
    if parsed.scheme or parsed.netloc or parsed.query or parsed.fragment:
        raise ValueError("nonlocal glTF URI")
    path = unquote(parsed.path, errors="strict")
    if not path or path.startswith("/") or "\\" in path or ":" in path or any(ord(c) < 32 for c in path):
        raise ValueError("unsafe glTF URI")
    if "/" in path and path.count("/") != parsed.path.count("/"):
        raise ValueError("encoded path separator")
    target = posixpath.normpath(posixpath.join(posixpath.dirname(source), path))
    if target in (".", "..") or target.startswith("../"):
        raise ValueError("glTF URI escapes repository")
    return target

def gltf_document(file):
    """Read external dependency declarations from glTF JSON or the GLB JSON chunk."""
    suffix=file.suffix.lower()
    if suffix==".gltf":
        return json.loads(file.read_text(encoding="utf-8"))
    if suffix!=".glb":
        return None
    with file.open("rb") as stream:
        header=stream.read(12)
        if header[:4]!=b"glTF":
            # Non-GLB files still belong to discovery; geometry validation is separate.
            return None
        require(len(header)==12,"truncated GLB header")
        magic,version,total=struct.unpack("<4sII",header)
        require(version==2 and total==file.stat().st_size,"invalid GLB header")
        chunk=stream.read(8)
        require(len(chunk)==8,"truncated GLB JSON chunk")
        length,kind=struct.unpack("<I4s",chunk)
        require(kind==b"JSON" and length%4==0 and 20+length<=total,"invalid GLB JSON chunk")
        return json.loads(stream.read(length).decode("utf-8"))

def runtime_resource_paths(sample):
    """Extract real resource paths from sampled nodes and effective materials."""
    for node in sample["nodes"]:
        mesh = node.get("mesh") or {}
        audio = node.get("audio") or {}
        values = [mesh.get("path"), audio.get("path"),node.get("scene"),mesh.get("skin_path"),(node.get("collision") or {}).get("path")]
        material = node.get("canvas_material") or {}
        values.extend((material.get("path"),material.get("shader")))
        for surf in mesh.get("surfaces", []):
            mat=surf.get("effective_material") or {}
            values.extend((mat.get("path"),mat.get("shader")))
            for key, value in mat.items():
                if key.endswith("_texture") and isinstance(value, dict):
                    values.append(value.get("path"))
        for value in values:
            if isinstance(value, str) and value.startswith("res://"):
                yield value[6:].split("::", 1)[0]

def sample_metrics(sample):
    """Measured counts of the entire sampled subtree, not per-asset budgets."""
    nodes=sample["nodes"]
    meshes=[n["mesh"] for n in nodes if n.get("mesh") and not n["mesh"].get("missing")]
    surfaces=[surf for mesh in meshes for surf in mesh.get("surfaces",[])]
    collisions=[n for n in nodes if n.get("collision") and not n["collision"].get("missing")]
    enabled=[n for n in collisions if not n["collision"].get("disabled",False)]
    triangles=[surf.get("triangles") for surf in surfaces]
    return {"id":sample["id"],"families":sorted(sample["families"]),
            "scope":"whole_sample_subtree","context":sample.get("context",{}),
            "nodes":len(nodes),"mesh_nodes":len(meshes),"surfaces":len(surfaces),
            "vertices":sum(surf.get("vertices",0) for surf in surfaces),
            "triangles":sum(t for t in triangles if t is not None),
            "unknown_triangle_surfaces":sum(t is None for t in triangles),
            "enabled_colliders":len(enabled),"disabled_colliders":len(collisions)-len(enabled),
            "collision_classes":dict(sorted(Counter(n["collision"]["class"] for n in enabled).items())),
            "lod_bias_counts":dict(sorted(Counter(str(m["lod_bias"]) for m in meshes if "lod_bias" in m).items())),
            "lod_indices_measured":False,"approved":False}

def category(p):
    suffix=Path(p).suffix.lower()
    if suffix in (".glb",".gltf") and p.startswith("assets/models/"):
        return "weapon_mesh"
    if suffix in (".glb",".gltf") and p.startswith("assets/characters/"):
        return "character_mesh"
    return EXT.get(suffix,"unclassified")

def preview(p):
    ext=Path(p).suffix.lower()
    if ext in (".glb",".gltf"):
        return {"mode":"direct_gltf","resource":p,"fidelity":"original_file_only"}
    if ext in (".tscn",".scn"):
        return {"mode":"runtime_capture","resource":p,"fidelity":"composition_pending"}
    return {"mode":"resource_inspection","resource":p,"fidelity":"original_file_only"}

def build(root,paths=None,runtime=None,revision=None):
    root=Path(root).resolve()
    paths=discover_paths(root) if paths is None else sorted(set(paths))
    revision=revision or git(root,"rev-parse","HEAD").decode().strip()
    baseline_path="assets/catalog/manifest.json"
    baseline=json.loads(safe(root,baseline_path).read_text(encoding="utf-8"))
    known=baseline["resources"]
    assets=copy.deepcopy(baseline["assets"])
    byid={a["id"]:a for a in assets}
    require(len(byid)==len(assets),"duplicate baseline asset ID")
    candidates={p for p in paths if p.startswith(("assets/","scenes/")) and p!=baseline_path and not p.startswith("assets/catalog/")}
    candidates|={p for p in paths if p.startswith("scripts/") and Path(p).suffix in (".gdshader",".gdshaderinc")}
    sources={p for p in paths if p.startswith(("scripts/","scenes/","assets/")) and Path(p).suffix in (".gd",".gdshader",".gdshaderinc",".tscn",".tres")}
    sources|={p for p in baseline["source_registry"] if p in paths}
    if "project.godot" in paths: sources.add("project.godot")
    refs=defaultdict(list)
    missing=[]
    dynamic=[]
    possible=[]
    # Iteratively discover references from newly discovered resource descriptors.
    queue=sorted(sources)
    seen=set()
    while queue:
        p=queue.pop(0)
        if p in seen: continue
        seen.add(p)
        f=safe(root,p)
        if not f.is_file(): continue
        if f.suffix.lower() not in (".gd",".gdshader",".gdshaderinc",".tscn",".tres",".godot",".gltf"): continue
        text=f.read_text(encoding="utf-8")
        if p.startswith("scripts/") and PROCEDURAL.search(text):
            possible.append(p)
        for line_no,line in enumerate(text.splitlines(),1):
            for match in REF.finditer(line):
                target=match.group(1).split("::",1)[0]
                rec={"source":p,"line":line_no,"target":target}
                if DYNAMIC.search(target):
                    dynamic.append(rec);continue
                # res:// literal directories are not asset references.
                try: targetfile=safe(root,target)
                except ValueError:
                    missing.append(rec);continue
                if targetfile.is_dir(): continue
                if not targetfile.is_file():
                    missing.append(rec);continue
                refs[target].append({"source":p,"line":line_no})
                if targetfile.suffix.lower() in (".gd",".gdshader",".gdshaderinc",".tscn",".tres",".gltf"):
                    sources.add(target);queue.append(target)
                if targetfile.suffix.lower() in EXT:
                    candidates.add(target)
    # Discover paths observed by the real engine before building resource records.
    runtime_gaps = []
    if runtime is not None:
        require(runtime.get("kind")=="frontline_runtime_inventory" and runtime.get("schema_version")==1 and not runtime.get("failures"),"invalid runtime evidence")
        require(runtime.get("commit")==revision,"stale runtime capture")
        for sample in runtime["samples"]:
            for p in sorted(set(runtime_resource_paths(sample))):
                try:
                    exists = safe(root,p).is_file()
                except ValueError:
                    exists = False
                if exists:
                    candidates.add(p)
                else:
                    runtime_gaps.append({"sample":sample["id"],"path":p,"reason":"not a local file"})
    # GLTF external relative buffers/images also belong to the catalog.
    gltf_dependencies = defaultdict(list)
    for p in sorted(candidates):
        if Path(p).suffix.lower() not in (".gltf",".glb"): continue
        f=safe(root,p)
        if not f.is_file(): continue
        d=gltf_document(f)
        if d is None: continue
        for item in d.get("buffers",[])+d.get("images",[]):
            uri=item.get("uri")
            if uri is None or isinstance(uri,str) and uri.startswith("data:"): continue
            try:
                q = resolve_gltf_uri(p, uri)
                exists = safe(root,q).is_file()
            except (ValueError, UnicodeError):
                exists = False
            if exists:
                candidates.add(q)
                refs[q].append({"source":p,"line":None})
                gltf_dependencies[p].append({"uri":uri,"path":q})
            else:
                missing.append({"source":p,"line":None,"target":uri})

    resources={}
    for p in sorted(candidates|set(known)):
        f=safe(root,p)
        old=known.get(p)
        if not f.is_file():
            resources[p]={"category":old["category"] if old else category(p),"status":"missing","references":refs[p],"sha256":None}
            continue
        fp=fingerprint(root,p)
        unchanged=bool(old and fp["git_blob_sha1"]==old["git_blob_sha1"])
        resources[p]={**fp,"category":old["category"] if old else category(p),
                      "status":"unchanged" if unchanged else "changed" if old else "new",
                      "references":refs[p],"provenance":old.get("provenance") if unchanged else None,
                      "observations":[]}
    for p, deps in sorted(gltf_dependencies.items()):
        resources[p]["gltf_dependencies"] = sorted(
            { (d["uri"], d["path"]) for d in deps })
        resources[p]["gltf_dependencies"] = [
            {"uri":uri,"path":path} for uri,path in resources[p]["gltf_dependencies"]]
    source_records={}
    for p in sorted(sources|set(baseline["source_registry"])):
        f=safe(root,p)
        source_records[p]=fingerprint(root,p) if f.is_file() else None
    owners=defaultdict(list)
    for a in assets:
        for out in a["outputs"]: owners[out["path"]].append(a["id"])
        a["validation"]["approved"]=False
        a["validation"]["runtime"]="not_observed_current"
        a["source_current"]=source_records.get(a["source"]["path"],resources.get(a["source"]["path"]))
        a["source_changed"]=not a["source_current"] or a["source_current"].get("git_blob_sha1")!=a["source"].get("git_blob_sha1")
        a["runtime_samples"]=[]
    # Discover physical files not already owned, including unknown formats.
    # import sidecars remain physical records; they aren't separate models.
    for p,rec in resources.items():
        if p in owners or rec["category"]=="import_metadata": continue
        id="file:"+p
        require(id not in byid,"discovery ID collision")
        a={"id":id,"category":rec["category"],"usage":"referenced" if refs[p] else "unverified",
           "source":{"path":p,"kind":"discovered_file","editable":None},
           "source_current":rec,"source_changed":None,"outputs":[{"path":p,"role":"resource"}],
           "preview":preview(p),"dependencies":{"resources":[],"assets":[],"sources":[]},
           "coordinates":None,"dimensions_m":None,"bounds_m":None,"pivots":None,"hierarchy":None,
           "animations":None,"collision":None,"lods":None,"materials":None,"budget":None,
           "provenance":rec.get("provenance"),"validation":{"approved":False,"runtime":"not_observed_current","studio_visual":"pending","godot_visual":"pending"},"runtime_samples":[]}
        assets.append(a);byid[id]=a;owners[p].append(id)
    known_procedural={a["source"]["path"] for a in assets if a["source"].get("kind")=="godot_recipe"}
    runtime_candidates=sorted(set(possible)-known_procedural)
    for p in runtime_candidates:
        id="candidate:"+p
        a={"id":id,"category":"procedural_candidate","usage":"unverified",
           "source":{"path":p,"kind":"heuristic_candidate","editable":True},"source_current":source_records[p],
           "outputs":[],"preview":{"mode":"runtime_capture","resource":None,"fidelity":"pending_capture"},
           "dependencies":{"resources":[],"assets":[],"sources":[]},"runtime_samples":[],
           "validation":{"approved":False,"runtime":"not_observed_current","studio_visual":"pending","godot_visual":"pending"}}
        assets.append(a);byid[id]=a
    runtime_summary=None
    runtime_samples={}
    dynamic_resolution=[]; geometry_index={}; runtime_compositions={}
    if runtime is not None:
        require(runtime.get("kind")=="frontline_runtime_inventory" and runtime.get("schema_version")==1 and not runtime.get("failures"),"invalid runtime evidence")
        require(runtime.get("commit")==revision,"stale runtime capture")
        # A working tree different from HEAD cannot inherit CI capture.
        regenerated_import_metadata=[]
        observed_paths = {p for sample in runtime["samples"] for p in runtime_resource_paths(sample) if p in resources and resources[p]["status"] != "missing"}
        for p in sorted(set(known)|set(baseline["source_registry"])|observed_paths|set(sources)):
            fp=resources.get(p) if p in resources else source_records.get(p)
            try:
                expected=git(root,"rev-parse",revision+":"+p).decode().strip()
            except subprocess.CalledProcessError as exc:
                raise ValueError("runtime source not tracked at revision: "+p) from exc
            if fp and fp.get("git_blob_sha1")==expected:
                continue
            # Godot can regenerate sidecars during --import. Keep both hashes
            # and never waive drift for actual meshes, textures or source code.
            if p in known and known[p]["category"]=="import_metadata" and fp and fp.get("git_blob_sha1"):
                regenerated_import_metadata.append({"path":p,"revision_blob":expected,"current_blob":fp["git_blob_sha1"]})
                continue
            raise ValueError("runtime source drift: "+p)
        sample_ids=set()
        for s in runtime["samples"]:
            require(s["id"] not in sample_ids,"duplicate runtime sample")
            sample_ids.add(s["id"])
            runtime_samples[s["id"]]=sample_metrics(s)
            observed={p for p in runtime_resource_paths(s) if p in resources and resources[p]["status"]!="missing"}
            for p in sorted(observed):
                resources[p]["observations"].append(s["id"])
            ids=set(s["families"])|{id for p in observed for id in owners[p]}
            for id in sorted(ids):
                require(id in byid,"unregistered runtime family: "+id)
                byid[id]["runtime_samples"].append(s["id"])
                byid[id]["validation"]["runtime"]="sampled"
        for q in runtime["query_records"]:
            require(q["family"] in byid,"unregistered query family")
            a=byid[q["family"]]
            a["validation"]["runtime"]="query_executed" if q["executed"] else "not_observed_current"
            a["query_evidence"]=q
        dynamic_resolution=dynamic_evidence(dynamic,runtime,resources,{s["id"]:set(runtime_resource_paths(s)) for s in runtime["samples"]})
        geometry_index,runtime_compositions=geometry_evidence(runtime)
        for id,comp in runtime_compositions.items():
            runtime_samples[id]["procedural_buffer_count"]=len({h for n in comp["nodes"] for h in n["buffer_sha256"]})
            runtime_samples[id]["composition_available"]=True
        runtime_summary={"commit":revision,"sha256":sha(canonical(runtime)),"samples":len(sample_ids),
                         "limitations":runtime["limitations"],"regenerated_import_metadata":regenerated_import_metadata,"approved":False}
    for a in assets:
        a["outputs_current"]=[{"path":o["path"],"status":resources.get(o["path"],{}).get("status","missing")} for o in a["outputs"]]
        p=a["preview"].get("resource")
        if p and (p not in resources or resources[p]["status"]=="missing"):
            a["preview"]={"mode":"unavailable","resource":None,"fidelity":"missing_resource"}
    assets.sort(key=lambda a:a["id"])
    return {"schema_version":1,"kind":"frontline_live_catalog","revision":revision,
            "baseline_sha256":sha(safe(root,baseline_path).read_bytes()),
            "assets":assets,"resources":resources,"sources":source_records,
            "missing_literal_references":missing,"dynamic_references":dynamic,
            "known_dynamic_gaps":baseline["known_dynamic_gaps"],"runtime_candidates":runtime_candidates,
            "runtime":runtime_summary,"runtime_samples":runtime_samples,"runtime_resource_gaps":runtime_gaps,"approved":False,
            "dynamic_resolution":dynamic_resolution,"geometry_index":geometry_index,"runtime_compositions":runtime_compositions,
            "geometry_payload":"runtime_geometry.json" if geometry_index else None,
            "counts":{"assets":len(assets),"resources":len(resources),"categories":dict(Counter(a["category"] for a in assets)),
                      "resource_status":dict(Counter(r["status"] for r in resources.values())),
                      "runtime_sampled_assets":sum(a["validation"]["runtime"] in ("sampled","query_executed") for a in assets)}}

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--root",default=str(Path(__file__).resolve().parents[2]))
    p.add_argument("--output",required=True)
    p.add_argument("--runtime")
    args=p.parse_args()
    runtime=json.loads(Path(args.runtime).read_text(encoding="utf-8")) if args.runtime else None
    data=build(args.root,runtime=runtime)
    out=Path(args.output)
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_bytes(canonical(data))
    print("LIVE_CATALOG_PASS",json.dumps(data["counts"],sort_keys=True))
    print("LIVE_CATALOG_GAPS",len(data["missing_literal_references"]),len(data["dynamic_references"]),len(data["runtime_candidates"]))
if __name__=="__main__":main()
