"""Reconcile finite formatted paths and actual Godot procedural mesh buffers.
Godot Variant data is opaque here; integrity is checked byte-for-byte.
No geometry or material is fabricated or considered visually approved.
"""
import base64
import hashlib
from collections import defaultdict

def require(ok,msg):
    if not ok: raise ValueError(msg)

def dynamic_evidence(refs,runtime,resources,observed_by_sample):
    probes=defaultdict(list)
    for row in runtime.get("dynamic_probes",[]):
        key=(row["source"],row["pattern"])
        args=row["arguments"]
        require(isinstance(args,list) and all(isinstance(a,str) for a in args),"invalid probe arguments")
        require(row["pattern"] % tuple(args)==row["path"],"dynamic expansion mismatch")
        require(type(row["exists"]) is bool and type(row["guarded"]) is bool,"invalid probe flags")
        exists=row["path"] in resources and resources[row["path"]]["status"]!="missing"
        require(exists==row["exists"],"dynamic probe file disagreement "+row["path"])
        prefix={"scripts/enemy.gd":"enemy_","scripts/loot_pickup.gd":"loot_weapon_","scripts/player.gd":"fps_"}.get(row["source"])
        ids=sorted(s for s,paths in observed_by_sample.items() if prefix and s.startswith(prefix) and row["path"] in paths)
        probes[key].append({**row,"observed_samples":ids,"sha256":resources[row["path"]]["sha256"] if exists else None})
    results=[]
    for ref in refs:
        key=(ref["source"],ref["target"])
        rows=sorted(probes.get(key,[]),key=lambda x:tuple(x["arguments"]))
        require(len({tuple(x["arguments"]) for x in rows})==len(rows),"duplicate dynamic probe")
        require(all(x["exists"] or x["guarded"] for x in rows),"unguarded missing probe")
        results.append({**ref,"status":"finite_domain_probed" if rows else "unresolved",
                        "domain_scope":"sampled weapon IDs and part names, not arbitrary script arguments",
                        "candidates":rows})
    require(set(probes)<= {(r["source"],r["target"]) for r in refs},"stale dynamic probe pattern")
    return results

def geometry_evidence(runtime):
    buffers=runtime.get("geometry_buffers",{})
    if "geometry_buffers" not in runtime:
        return {},{}
    index={}
    for digest,row in sorted(buffers.items()):
        require(row["encoding"]=="godot_variant_v4_base64","unknown geometry encoding")
        data=base64.b64decode(row["data"],validate=True)
        require(len(data)==row["bytes"] and hashlib.sha256(data).hexdigest()==digest,"geometry buffer integrity")
        index[digest]={k:v for k,v in row.items() if k!="data"}
        index[digest]["sample_ids"]=[]
    compositions={}
    for sample in runtime["samples"]:
        nodes=[]
        for node in sample["nodes"]:
            mesh=node.get("mesh") or {}
            if not mesh or mesh.get("missing"):continue
            hashes=[]
            for surf in mesh.get("surfaces",[]):
                digest=surf.get("buffer_sha256")
                if not mesh.get("path"):
                    require(digest in index,"missing procedural surface buffer")
                if digest:
                    require(digest in index,"unknown buffer reference")
                    require(index[digest]["primitive"]==surf.get("primitive"),"buffer primitive mismatch")
                    if sample["id"] not in index[digest]["sample_ids"]:
                        index[digest]["sample_ids"].append(sample["id"])
                    hashes.append(digest)
            nodes.append({"path":node["path"],"mesh_resource":mesh.get("path"),"buffer_sha256":hashes,
                          "world":node.get("world"),"visible_in_tree":node.get("visible_in_tree")})
        compositions[sample["id"]]={"scope":"sampled_mesh_nodes","nodes":nodes,"approved":False}
    # Some buffers are collected in a discarded repeat snapshot; retain them
    # explicitly as unreferenced rather than claiming they are part of a sample.
    return index,compositions
