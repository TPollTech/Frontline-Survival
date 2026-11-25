"""Validate portable native surface arrays before serving them to the browser."""
import base64, math, struct
from tools.asset_pipeline.live_catalog import canonical,sha

def require(ok,msg):
    if not ok: raise ValueError(msg)

def raw(row):
    b=base64.b64decode(row["data"],validate=True)
    require(len(b)==row["bytes"] and sha(b)==row["sha256"],"portable attribute integrity")
    return b

def stage(runtime,catalog,out):
    buffers=runtime["studio_buffers"]; textures=runtime["studio_textures"]
    require(buffers,"missing portable surface buffers")
    require(set(runtime["geometry_buffers"])<=set(buffers),"registered procedural or LOD buffer not portable")
    measured={}
    for digest,b in buffers.items():
        a=b["attributes"]; positions=raw(a["position"])
        require(len(positions)%12==0 and len(positions)>0,"position stride")
        n=len(positions)//12
        for name,row in a.items():
            data=raw(row)
            stride={"position":12,"normal":12,"uv":8,"uv1":8,"tangent":16,"color":16,"index":4,"joints":4,"weights":4}[name]
            require(len(data)%stride==0,"attribute stride")
            if name not in ("index","joints","weights"):
                require(len(data)==n*stride,"attribute count")
            if name=="index":
                require(all(0<=i[0]<n for i in struct.iter_unpack("<i",data)),"index out of range")
            elif name!="joints":
                require(all(math.isfinite(f[0]) for f in struct.iter_unpack("<f",data)),"nonfinite array")
        measured[digest]=(n,a.get("index",{}).get("bytes",0)//4,b["primitive"])
    for digest,t in textures.items():
        b=base64.b64decode(t["data"],validate=True)
        require(len(b)==t["bytes"] and sha(b)==digest and b[:8]==b"\x89PNG\r\n\x1a\n","texture integrity")
    for assembly in runtime.get("registered_world_lods",[]):
        for level in assembly["levels"]:
            tris=sum((measured[h][1] or measured[h][0])//3 for h in level["buffer_sha256"])
            require(tris*len(assembly["parts"])==level["assembly_triangles"],"registered LOD triangle mismatch")
    coverage=[]
    for sample in runtime["samples"]:
        total=visible=triangles=0;unsupported=0;skinned=0
        for node in sample["nodes"]:
            mesh=node.get("mesh") or {}
            if mesh.get("missing"):continue
            for surface in mesh.get("surfaces",[]):
                digest=surface["studio_sha256"]
                require(digest in measured,"missing surface")
                n,i,p=measured[digest]
                require((n,i,p)==(surface["vertices"],surface["indices"],surface["primitive"]),"native metrics mismatch")
                if surface.get("buffer_sha256"):
                    require(surface["buffer_sha256"]==digest and digest in runtime["geometry_buffers"],"procedural source linkage")
                total+=1
                if node.get("visible_in_tree"):
                    visible+=1
                    if p==3:triangles+=surface["triangles"]
                    else:unsupported+=1
                    if mesh.get("has_skin"):skinned+=1
        coverage.append({"id":sample["id"],"surfaces":total,"visible_surfaces":visible,"visible_triangles":triangles,"unsupported_visible":unsupported,"skinned_visible":skinned})
    payload=canonical({"kind":"frontline_studio_surfaces","revision":catalog["revision"],"buffers":buffers,"textures":textures,"coverage":coverage})
    (out/"runtime_surfaces.json").write_bytes(payload)
    catalog.update({"surface_payload":"runtime_surfaces.json","surface_payload_sha256":sha(payload),"surface_coverage":coverage})
    print("STUDIO_SURFACE_STAGE_PASS",len(buffers),len(textures),len(coverage))
