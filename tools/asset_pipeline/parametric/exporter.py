"""Deterministic glTF 2.0 / GLB export of the canonical neutral IR.

No Blender/Godot dependency in serialization. No timestamps or absolute paths.
UV source convention is V-up; glTF V-down requires flipping V, tangent w and
normal texture green channel together. Coordinates already match glTF Y-up RH.
"""
from dataclasses import asdict
from pathlib import Path, PurePosixPath
import base64
import hashlib
import json
import math
import struct
from .model import SceneSpec, require, dot
from .shading import RenderMesh
from .pbr import PBRMaterial, MaterialLibrary, _png
from .rig import RigSpec

def canonical(data):
    return json.dumps(data,sort_keys=True,separators=(",",":"),allow_nan=False).encode("utf-8")

def digest(data):
    return hashlib.sha256(data).hexdigest()

def source_manifest(root,paths,revision):
    """Hash actual input files, not just filenames; refuse traversal/symlinks."""
    require(isinstance(revision,str) and bool(revision.strip()),"missing source revision")
    root=Path(root).resolve()
    entries=[]
    for name in sorted(set(paths)):
        p=PurePosixPath(name)
        require(not p.is_absolute() and ".." not in p.parts and "\\" not in name and ":" not in name and str(p)==name,"unsafe source path")
        f=root.joinpath(*p.parts)
        require(f.is_file() and f.resolve().is_relative_to(root) and not any(root.joinpath(*p.parts[:i]).is_symlink() for i in range(1,len(p.parts)+1)),"missing or symlink source")
        entries.append({"path":name,"sha256":digest(f.read_bytes())})
    require(bool(entries),"source files required")
    return {"revision":revision,"files":entries}

class Buffer:
    def __init__(self):
        self.data=bytearray()
        self.views=[]
        self.accessors=[]
    def view(self,data,target=None):
        self.data.extend(b"\0"*((-len(self.data))%4))
        v={"buffer":0,"byteOffset":len(self.data),"byteLength":len(data)}
        if target is not None:
            v["target"]=target
        self.views.append(v)
        self.data.extend(data)
        return len(self.views)-1
    def accessor(self,rows,kind,component=5126,target=None,limits=False):
        n={"SCALAR":1,"VEC2":2,"VEC3":3,"VEC4":4,"MAT4":16}[kind]
        fmt={5126:"f",5123:"H",5125:"I"}[component]
        rows=tuple(tuple(row) for row in rows)
        require(bool(rows) and all(len(row)==n for row in rows),"invalid accessor shape")
        raw=b"".join(struct.pack("<"+fmt*n,*row) for row in rows)
        # Bounds must describe the serialized floats, not their float64 inputs.
        a={"bufferView":self.view(raw,target),"componentType":component,"count":len(rows),"type":kind}
        if limits:
            values=list(struct.iter_unpack("<"+fmt*n,raw))
            a["min"]=[min(r[i] for r in values) for i in range(n)]
            a["max"]=[max(r[i] for r in values) for i in range(n)]
        self.accessors.append(a)
        return len(self.accessors)-1

def matrix(t):
    m=t.matrix
    cols=(m[:3],m[4:7],m[8:11])
    require(all(abs(dot(a,b))<=1e-7*math.sqrt(dot(a,a)*dot(b,b)) for i,a in enumerate(cols) for b in cols[i+1:]),"glTF node cannot contain shear")
    return list(m)

def encode(scene,render_meshes,library,*,sources,rig=None):
    require(isinstance(scene,SceneSpec) and isinstance(library,MaterialLibrary),"invalid export inputs")
    require(isinstance(sources,dict) and isinstance(sources.get("revision"),str) and bool(sources.get("files")),"source manifest required")
    renders={r.mesh.id:r for r in render_meshes}
    require(all(isinstance(r,RenderMesh) for r in renders.values()) and len(renders)==len(render_meshes),"duplicate render mesh")
    used={n.mesh_id for n in scene.nodes if n.mesh_id}
    mesh_by={m.id:m for m in scene.meshes}
    require(set(renders)==used and all(r.mesh==mesh_by[k] for k,r in renders.items()),"render/source mismatch")
    require(rig is None or isinstance(rig,RigSpec) and rig.scene==scene,"rig scene mismatch")
    lib_materials={m.id:m for m in library.materials}
    tex_by={t.id:t for t in library.textures}
    buf=Buffer()
    doc={"asset":{"version":"2.0","generator":"Frontline parametric exporter v1"},"scene":0,"scenes":[{"name":scene.id,"nodes":[]}],"nodes":[],"meshes":[]}
    material_indices={}
    texture_indices={}
    def texture(id):
        if id in texture_indices:
            return texture_indices[id]
        require(id in tex_by,"missing texture")
        t=tex_by[id]
        rgb=t.rgb
        if t.role=="normal":
            data=bytearray(rgb)
            for i in range(1,len(data),3):
                data[i]=255-data[i]
            png=_png(t.width,t.height,bytes(data))
        else:
            png=t.png()
        images=doc.setdefault("images",[])
        images.append({"name":id,"bufferView":buf.view(png),"mimeType":"image/png",
                       "extras":{"source_sha256":digest(t.png()),"export_sha256":digest(png),"role":t.role,"source":t.source,"license":t.license}})
        textures=doc.setdefault("textures",[])
        textures.append({"source":len(images)-1,"sampler":0,"name":id})
        doc["samplers"]=[{"magFilter":9729,"minFilter":9987,"wrapS":10497,"wrapT":10497}]
        texture_indices[id]=len(textures)-1
        return texture_indices[id]
    for m in scene.materials:
        p={"baseColorFactor":m.base_color,"metallicFactor":m.metallic,"roughnessFactor":m.roughness}
        out={"name":m.id,"pbrMetallicRoughness":p}
        if isinstance(m,PBRMaterial):
            require(lib_materials.get(m.id)==m,"PBR material not in library")
            out.update({"emissiveFactor":m.emissive,"alphaMode":m.alpha_mode,"doubleSided":m.double_sided})
            if m.alpha_mode=="MASK":
                out["alphaCutoff"]=m.alpha_cutoff
            for role,id in m.texture_slots().items():
                require(id in tex_by and tex_by[id].role==role,"texture role mismatch")
                ref={"index":texture(id)}
                if role=="base_color":
                    p["baseColorTexture"]=ref
                elif role=="orm":
                    p["metallicRoughnessTexture"]=ref
                    out["occlusionTexture"]={**ref,"strength":m.occlusion_strength}
                elif role=="normal":
                    out["normalTexture"]={**ref,"scale":m.normal_scale}
                else:
                    out["emissiveTexture"]=ref
        mats=doc.setdefault("materials",[])
        material_indices[m.id]=len(mats)
        mats.append(out)
    skin_by={s.mesh_id:s for s in rig.skins} if rig else {}
    joint_order={b.id:i for i,b in enumerate(rig.skeleton.bones)} if rig else {}
    mesh_indices={}
    attributes={}
    for n in scene.nodes:
        if n.mesh_id is None:
            continue
        key=(n.mesh_id,n.material_id)
        if key in mesh_indices:
            continue
        r=renders[n.mesh_id]
        if n.mesh_id not in attributes:
            attrs={"POSITION":buf.accessor(r.positions,"VEC3",target=34962,limits=True),
                   "NORMAL":buf.accessor(r.normals,"VEC3",target=34962),
                   "TEXCOORD_0":buf.accessor(((u,1-v) for u,v in r.uv),"VEC2",target=34962),
                   "TANGENT":buf.accessor(((*t[:3],-t[3]) for t in r.tangents),"VEC4",target=34962)}
            if n.mesh_id in skin_by:
                rows=skin_by[n.mesh_id].render_weights(r,rig.skeleton)
                attrs["JOINTS_0"]=buf.accessor((tuple(joint_order[b] for b,w in row)+(0,)*(4-len(row)) for row in rows),"VEC4",5123,34962)
                attrs["WEIGHTS_0"]=buf.accessor((tuple(w for b,w in row)+(0.,)*(4-len(row)) for row in rows),"VEC4",target=34962)
            idx=buf.accessor(((i,) for i in r.indices),"SCALAR",5123 if max(r.indices)<65536 else 5125,34963,True)
            attributes[n.mesh_id]=(attrs,idx)
        attrs,idx=attributes[n.mesh_id]
        primitive={"attributes":attrs,"indices":idx,"mode":4}
        if n.material_id:
            primitive["material"]=material_indices[n.material_id]
        mesh_indices[key]=len(doc["meshes"])
        doc["meshes"].append({"name":n.mesh_id,"primitives":[primitive]})
    node_indices={n.id:i for i,n in enumerate(scene.nodes)}
    def link(child,parent):
        if parent is None:
            doc["scenes"][0]["nodes"].append(child)
        else:
            doc["nodes"][parent].setdefault("children",[]).append(child)
    for n in scene.nodes:
        out={"name":n.id,"matrix":matrix(n.local)}
        if n.mesh_id:
            out["mesh"]=mesh_indices[(n.mesh_id,n.material_id)]
            if n.mesh_id in skin_by:
                out["skin"]=0
        doc["nodes"].append(out)
    for n in scene.nodes:
        link(node_indices[n.id],node_indices[n.parent_id] if n.parent_id else None)
    if rig:
        bones=rig.skeleton.bones
        joints={}
        for bone in bones:
            joints[bone.id]=len(doc["nodes"])
            doc["nodes"].append({"name":"bone:"+bone.id,"matrix":matrix(bone.rest_local),"extras":{"length_m":bone.length_m}})
            link(joints[bone.id],joints[bone.parent_id] if bone.parent_id else node_indices[rig.anchor_node_id])
        if rig.skins:
            bind=rig.skeleton.inverse_bind()
            doc["skins"]=[{"name":rig.skeleton.id,"joints":[joints[b.id] for b in bones],
                "skeleton":joints[bones[0].id],"inverseBindMatrices":buf.accessor((bind[b.id].matrix for b in bones),"MAT4")}]
        for s in rig.sockets:
            i=len(doc["nodes"])
            doc["nodes"].append({"name":"socket:"+s.id,"matrix":matrix(s.local),"extras":{"socket":s.id}})
            link(i,(joints if s.owner_kind=="bone" else node_indices)[s.owner_id])
    require(bool(doc["meshes"]),"no exportable mesh")
    buf.data.extend(b"\0"*((-len(buf.data))%4))
    doc.update({"buffers":[{"byteLength":len(buf.data)}],"bufferViews":buf.views,"accessors":buf.accessors})
    trace={"source":sources,"scene_sha256":scene.sha256(),"library_sha256":library.sha256(),
           "rig_sha256":rig.sha256() if rig else None,
           "render_sha256":digest(canonical([asdict(renders[k]) for k in sorted(renders)])),
           "uv_conversion":"v=1-v; tangent.w=-w; normal green=255-g","approved":False}
    doc["asset"]["extras"]={"frontline":trace}
    return doc,bytes(buf.data),trace

def export_bundle(scene,render_meshes,library,*,sources,rig=None):
    doc,bin,trace=encode(scene,render_meshes,library,sources=sources,rig=rig)
    js=canonical(doc)
    js+=b" "*((-len(js))%4)
    glb=struct.pack("<4sII",b"glTF",2,12+8+len(js)+8+len(bin))+struct.pack("<I4s",len(js),b"JSON")+js+struct.pack("<I4s",len(bin),b"BIN\0")+bin
    doc["buffers"][0]["uri"]="data:application/octet-stream;base64,"+base64.b64encode(bin).decode("ascii")
    gltf=canonical(doc)+b"\n"
    files={"asset.glb":glb,"asset.gltf":gltf}
    files["export.json"]=canonical({"schema_version":1,"trace":trace,"outputs":{k:{"sha256":digest(v),"bytes":len(v)} for k,v in files.items()}})+b"\n"
    return files

def write_bundle(directory,files):
    p=Path(directory)
    p.mkdir(parents=True,exist_ok=True)
    require(not any(p.iterdir()),"export directory must be empty")
    require(set(files)=={"asset.glb","asset.gltf","export.json"},"unexpected bundle members")
    for name,data in sorted(files.items()):
        (p/name).write_bytes(data)

def verify_bundle(directory,expected):
    p=Path(directory)
    require({f.name for f in p.iterdir()}==set(expected),"unexpected bundle members")
    require(all((p/name).read_bytes()==data for name,data in expected.items()),"bundle mismatch")
    return True
