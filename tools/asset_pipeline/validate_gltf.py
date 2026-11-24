"""Read-only glTF/GLB technical validation, deterministic reports, no visual approval."""
import argparse, base64, hashlib, json, math, struct, re
from pathlib import Path
from collections import Counter
from tools.asset_pipeline.live_catalog import build, canonical, safe, resolve_gltf_uri
from tools.asset_pipeline.parametric.lod import BUDGETS

COMP={5120:("b",1),5121:("B",1),5122:("h",2),5123:("H",2),5125:("I",4),5126:("f",4)}
WIDTH={"SCALAR":1,"VEC2":2,"VEC3":3,"VEC4":4,"MAT2":4,"MAT3":9,"MAT4":16}
def require(ok,message):
    if not ok: raise ValueError(message)
def index(items,i):
    require(type(i) is int and 0<=i<len(items),"reference out of range: "+str(i))
    return items[i]
def finite(a):
    return all(isinstance(v,(int,float)) and not isinstance(v,bool) and math.isfinite(v) for v in a)
def digest(data): return hashlib.sha256(data).hexdigest()
def sub(a,b): return tuple(x-y for x,y in zip(a,b))
def dot(a,b): return sum(x*y for x,y in zip(a,b))
def cross(a,b): return (a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0])
def length(a): return math.sqrt(dot(a,a))
IDENTITY=(1,0,0,0,0,1,0,0,0,0,1,0,0,0,0,1)
def multiply(a,b):
    return tuple(sum(a[k*4+r]*b[c*4+k] for k in range(4)) for c in range(4) for r in range(4))
def matrix(node):
    if "matrix" in node:return tuple(node["matrix"])
    x,y,z,w=node.get("rotation",(0,0,0,1))
    sx,sy,sz=node.get("scale",(1,1,1))
    tx,ty,tz=node.get("translation",(0,0,0))
    return ((1-2*y*y-2*z*z)*sx,2*(x*y+z*w)*sx,2*(x*z-y*w)*sx,0,
            2*(x*y-z*w)*sy,(1-2*x*x-2*z*z)*sy,2*(y*z+x*w)*sy,0,
            2*(x*z+y*w)*sz,2*(y*z-x*w)*sz,(1-2*x*x-2*y*y)*sz,0,tx,ty,tz,1)
def point(m,v):
    return tuple(sum(m[c*4+r]*v[c] for c in range(3))+m[12+r] for r in range(3))
def parse_file(path):
    raw=path.read_bytes()
    if path.suffix.lower()==".gltf":
        return json.loads(raw),None
    require(len(raw)>=20,"truncated GLB")
    magic,version,total=struct.unpack_from("<4sII",raw)
    require(magic==b"glTF" and version==2 and total==len(raw),"invalid GLB header")
    pos=12;chunks=[]
    while pos<len(raw):
        require(pos+8<=len(raw),"truncated chunk header")
        size,kind=struct.unpack_from("<I4s",raw,pos);pos+=8
        require(size%4==0 and pos+size<=len(raw),"invalid GLB chunk size")
        chunks.append((kind,raw[pos:pos+size]));pos+=size
    require(chunks and chunks[0][0]==b"JSON" and sum(k==b"JSON" for k,_ in chunks)==1 and sum(k==b"BIN\0" for k,_ in chunks)<=1,"invalid GLB chunks")
    return json.loads(chunks[0][1]),next((v for k,v in chunks if k==b"BIN\0"),None)

class Audit:
    def __init__(self,root,path,category=None,strict=False,source_root=None,contract=None):
        self.root=Path(root).resolve();self.path=path;self.category=category;self.strict=strict;self.source_root=Path(source_root or root).resolve()
        self.errors=[];self.warnings=[];self.unknown=[];self.stats={};self.cache={};self.contract=contract
    def issue(self,code,detail,level="error"):
        getattr(self,{"error":"errors","warning":"warnings","unknown":"unknown"}[level]).append({"code":code,"detail":str(detail)})
    def conditional(self,code,detail):
        self.issue(code,detail,"error" if self.strict else "warning")
    def uri(self,uri):
        if uri.startswith("data:"):
            header,body=uri.split(",",1);require(header.endswith(";base64"),"unsupported non-base64 data URI")
            return base64.b64decode(body,validate=True)
        return safe(self.root,resolve_gltf_uri(self.path,uri)).read_bytes()
    def view(self,i):
        v=index(self.doc.get("bufferViews",[]),i);b=index(self.buffers,v["buffer"])
        offset=v.get("byteOffset",0);size=v["byteLength"]
        require(type(offset) is int and type(size) is int and offset>=0 and size>0 and offset+size<=len(b),"bufferView outside buffer")
        return memoryview(b)[offset:offset+size],v
    def values(self,i):
        if i in self.cache:return self.cache[i]
        a=index(self.doc.get("accessors",[]),i)
        if "sparse" in a: raise NotImplementedError("sparse accessor")
        fmt,component_size=COMP[a["componentType"]];n=WIDTH[a["type"]];count=a["count"]
        require(type(count) is int and 0<count<=10000000,"invalid accessor count")
        if "bufferView" not in a: raise NotImplementedError("accessor without bufferView")
        if a["type"] in ("MAT2","MAT3") and component_size<4:raise NotImplementedError("packed matrix accessor")
        b,v=self.view(a["bufferView"]);offset=a.get("byteOffset",0);stride=v.get("byteStride",n*component_size)
        require(type(offset) is int and type(stride) is int and offset>=0 and stride>=n*component_size and stride%component_size==0 and offset%component_size==0 and offset+(count-1)*stride+n*component_size<=len(b),"accessor outside bufferView")
        vals=[struct.unpack_from("<"+fmt*n,b,offset+j*stride) for j in range(count)]
        require(all(finite(x) for x in vals),"nonfinite accessor")
        if a.get("normalized"):
            require(a["componentType"] in (5120,5121,5122,5123),"invalid normalized component")
            mx={5120:127,5121:255,5122:32767,5123:65535}[a["componentType"]]
            vals=[tuple(max(-1,x/mx) for x in v) for v in vals]
        self.cache[i]=vals
        return vals
    def attr(self,attrs,name,size,count=None,components=None):
        if name not in attrs:return None
        ai=attrs[name];a=index(self.doc.get("accessors",[]),ai);v=self.values(ai)
        require(WIDTH[a["type"]]==size and (count is None or len(v)==count),"invalid "+name+" shape")
        if components is not None:require(a["componentType"] in components,"invalid "+name+" component type")
        return v
    def geometry(self):
        d=self.doc;metrics=[];used_materials=set()
        for mi,mesh in enumerate(d.get("meshes",[])):
            result={"vertices":0,"triangles":0,"slots":0,"unknown_topology":0,"positions":[]}
            for pi,p in enumerate(mesh["primitives"]):
                label=f"mesh {mi} primitive {pi}";attrs=p["attributes"]
                try:
                    positions=self.attr(attrs,"POSITION",3,components=(5126,))
                    require(positions is not None,"POSITION missing")
                    n=len(positions);result["vertices"]+=n;result["slots"]+=1;result["positions"].extend(positions)
                    normal=self.attr(attrs,"NORMAL",3,n)
                    if normal is None:self.conditional("NORMAL_MISSING",label)
                    elif any(abs(length(v)-1)>.03 for v in normal):self.conditional("NORMAL_LENGTH",label)
                    uv=self.attr(attrs,"TEXCOORD_0",2,n)
                    if "TEXCOORD_1" in attrs:self.attr(attrs,"TEXCOORD_1",2,n)
                    tangent=self.attr(attrs,"TANGENT",4,n)
                    if tangent and any(abs(length(v[:3])-1)>.03 or abs(abs(v[3])-1)>.03 for v in tangent):self.conditional("TANGENT_INVALID",label)
                    if "indices" in p:
                        a=index(d["accessors"],p["indices"])
                        require(a["type"]=="SCALAR" and a["componentType"] in (5121,5123,5125) and not a.get("normalized"),"invalid index accessor")
                        ids=[v[0] for v in self.values(p["indices"])]
                    else:ids=list(range(n))
                    require(all(0<=i<n for i in ids),"index outside POSITION")
                    mode=p.get("mode",4)
                    if mode==4:
                        require(len(ids)%3==0 and len(ids)>=3,"invalid triangle count")
                        result["triangles"]+=len(ids)//3
                        degenerate=inverted=0
                        for j in range(0,len(ids),3):
                            a,b,c=ids[j:j+3];face=cross(sub(positions[b],positions[a]),sub(positions[c],positions[a]))
                            if length(face)<=1e-14:degenerate+=1;continue
                            if normal and all(dot(face,normal[i]) < -length(face)*.05 for i in (a,b,c)):inverted+=1
                        if degenerate:self.conditional("DEGENERATE_TRIANGLES",f"{label}: {degenerate}")
                        if inverted:self.conditional("NORMAL_OPPOSES_WINDING",f"{label}: {inverted}")
                    else:
                        result["unknown_topology"]+=1;self.issue("TOPOLOGY_UNMEASURED",label+" mode "+str(mode),"unknown")
                    if "material" in p:
                        material=index(d.get("materials",[]),p["material"]);used_materials.add(p["material"])
                        refs=self.texture_infos(material)
                        for ref in refs:
                            index(d.get("textures",[]),ref["index"])
                            channel=ref.get("texCoord",0)
                            if "TEXCOORD_"+str(channel) not in attrs:self.conditional("TEXTURE_UV_MISSING",label+" channel "+str(channel))
                    elif self.strict:self.issue("MATERIAL_MISSING",label)
                    a=index(d["accessors"],attrs["POSITION"])
                    for k,op in (("min",min),("max",max)):
                        actual=[op(v[j] for v in positions) for j in range(3)]
                        if k not in a or len(a[k])!=3 or any(not math.isclose(x,y,abs_tol=1e-5,rel_tol=1e-5) for x,y in zip(actual,a[k])):self.conditional("POSITION_BOUNDS",label+" "+k)
                except NotImplementedError as e:self.issue("ACCESSOR_UNSUPPORTED",f"{label}: {e}","unknown")
                except (ValueError,KeyError,IndexError,TypeError,OverflowError,struct.error) as e:self.issue("GEOMETRY_INVALID",f"{label}: {e}")
            metrics.append(result)
        self.stats["mesh_definitions"]=len(metrics);self.stats["used_materials"]=len(used_materials)
        return metrics
    @staticmethod
    def texture_infos(material):
        p=material.get("pbrMetallicRoughness",{})
        return [x for x in (p.get("baseColorTexture"),p.get("metallicRoughnessTexture"),material.get("normalTexture"),material.get("occlusionTexture"),material.get("emissiveTexture")) if x is not None]
    def materials(self):
        d=self.doc
        for i,m in enumerate(d.get("materials",[])):
            p=m.get("pbrMetallicRoughness",{})
            for name,v in (("baseColorFactor",p.get("baseColorFactor",[1]*4)),("metallicFactor",[p.get("metallicFactor",1)]),("roughnessFactor",[p.get("roughnessFactor",1)]),("emissiveFactor",m.get("emissiveFactor",[0]*3))):
                expected={"baseColorFactor":4,"emissiveFactor":3}.get(name,1)
                if len(v)!=expected or not finite(v) or any(x<0 or x>1 for x in v):self.issue("PBR_FACTOR",f"material {i} {name}")
            if m.get("alphaMode","OPAQUE") not in ("OPAQUE","MASK","BLEND"):self.issue("ALPHA_MODE",i)
            for t in self.texture_infos(m):index(d.get("textures",[]),t["index"])
        for i,t in enumerate(d.get("textures",[])):
            if "source" in t:index(d.get("images",[]),t["source"])
            else:self.issue("TEXTURE_EXTENSION_SOURCE",i,"unknown")
            if "sampler" in t:index(d.get("samplers",[]),t["sampler"])
        for i,image in enumerate(d.get("images",[])):
            require(("uri" in image)!=("bufferView" in image),"image requires one source")
            data=self.uri(image["uri"]) if "uri" in image else bytes(self.view(image["bufferView"])[0])
            png=data.startswith(b"\x89PNG\r\n\x1a\n") and len(data)>=24 and data[12:16]==b"IHDR" and all(struct.unpack_from(">II",data,16))
            jpg=data.startswith(b"\xff\xd8") and data.endswith(b"\xff\xd9")
            webp=len(data)>=12 and data[:4]==b"RIFF" and data[8:12]==b"WEBP"
            ktx=data.startswith(b"\xabKTX 20\xbb\r\n\x1a\n")
            if not (png or jpg or webp or ktx):self.issue("IMAGE_SIGNATURE",i)
            mime=image.get("mimeType")
            if mime and not {"image/png":png,"image/jpeg":jpg,"image/webp":webp,"image/ktx2":ktx}.get(mime,False):self.issue("IMAGE_MIME",i)
        self.stats["textures"]=len(d.get("textures",[]));self.stats["materials"]=len(d.get("materials",[]))
    def hierarchy(self,metrics):
        d=self.doc;nodes=d.get("nodes",[]);parents={};visiting=set();done=set()
        for i,n in enumerate(nodes):
            if "matrix" in n:
                m=n["matrix"];require(len(m)==16 and finite(m) and all(abs(m[j]-v)<1e-6 for j,v in ((3,0),(7,0),(11,0),(15,1))),"invalid affine matrix")
                require(not any(k in n for k in ("translation","rotation","scale")),"matrix and TRS coexist")
                det=dot(m[:3],cross(m[4:7],m[8:11]))
                if abs(det)<1e-12:self.conditional("SINGULAR_TRANSFORM",i)
                elif det<0:self.issue("MIRRORED_TRANSFORM",i,"warning")
            else:
                for k,default in (("translation",[0]*3),("scale",[1]*3),("rotation",[0,0,0,1])):
                    v=n.get(k,default);require(len(v)==len(default) and finite(v),"invalid "+k)
                    if k=="scale" and any(abs(x)<1e-12 for x in v):self.conditional("SINGULAR_TRANSFORM",i)
                    if k=="rotation" and abs(length(v)-1)>.001:self.conditional("QUATERNION_LENGTH",i)
                    if k=="scale" and v[0]*v[1]*v[2]<0:self.issue("MIRRORED_TRANSFORM",i,"warning")
            if "mesh" in n:index(metrics,n["mesh"])
            if "skin" in n:index(d.get("skins",[]),n["skin"])
            if "camera" in n:index(d.get("cameras",[]),n["camera"])
            for child in n.get("children",[]):
                index(nodes,child);require(child not in parents,"multiple parents or duplicate child")
                parents[child]=i
        def walk(i):
            require(i not in visiting,"node hierarchy cycle")
            if i in done:return
            visiting.add(i)
            for c in nodes[i].get("children",[]):walk(c)
            visiting.remove(i);done.add(i)
        for i in range(len(nodes)):walk(i)
        scenes=d.get("scenes",[]);require(bool(scenes),"missing scene")
        selected=index(scenes,d.get("scene",0))
        for sc in scenes:
            for r in sc.get("nodes",[]):index(nodes,r);require(r not in parents,"scene root has parent")
        for sk in d.get("skins",[]):
            joints=sk["joints"];require(len(joints)>0 and len(set(joints))==len(joints),"invalid skin joints")
            for j in joints:index(nodes,j)
            if "skeleton" in sk:index(nodes,sk["skeleton"])
            if "inverseBindMatrices" in sk:
                a=index(d["accessors"],sk["inverseBindMatrices"]);require(a["type"]=="MAT4" and a["componentType"]==5126 and a["count"]>=len(joints),"invalid inverse bind matrices")
        for anim in d.get("animations",[]):
            for sampler in anim["samplers"]:
                index(d["accessors"],sampler["input"]);index(d["accessors"],sampler["output"])
            for ch in anim["channels"]:
                index(anim["samplers"],ch["sampler"])
                if "node" in ch["target"]:index(nodes,ch["target"]["node"])
        instances=[];lo=[math.inf]*3;hi=[-math.inf]*3;worlds={}
        def collect(i,parent):
            n=nodes[i];world=multiply(parent,matrix(n));worlds[i]=world
            if "mesh" in n:
                m=metrics[n["mesh"]];instances.append(m)
                for v in m["positions"]:
                    for j,x in enumerate(point(world,v)):
                        lo[j]=min(lo[j],x);hi[j]=max(hi[j],x)
            for c in n.get("children",[]):collect(c,world)
        for r in selected.get("nodes",[]):collect(r,IDENTITY)
        if all(math.isfinite(x) for x in lo+hi):
            self.stats["rest_geometry_aabb_m"]={"min":lo,"max":hi,"dimensions":[b-a for a,b in zip(lo,hi)],"scope":"undeformed vertex positions with node world transforms"}
            if max(b-a for a,b in zip(lo,hi))<=1e-9:self.conditional("ZERO_EXTENT","all dimensions zero")
        self.stats.update(nodes=len(nodes),mesh_instances=len(instances),vertices=sum(x["vertices"] for x in instances),triangles=sum(x["triangles"] for x in instances),material_slots=sum(x["slots"] for x in instances),unknown_topology=sum(x["unknown_topology"] for x in instances))
        if self.contract is not None:
            c=self.contract;require(c.get("unit")=="m" and c.get("up")=="+Y","contract must use canonical metres and Y up")
            tolerance=c.get("tolerance_m",.001)
            require(finite([tolerance]) and 0<tolerance<=.05,"invalid physical tolerance")
            def compare(actual,expected,tol,code,label):
                require(isinstance(expected,list) and len(actual)==len(expected) and finite(expected),"invalid contract "+label)
                if any(abs(a-b)>tol for a,b in zip(actual,expected)):self.issue(code,label+": "+str(actual)+" != "+str(expected))
            if "dimensions_m" in c:
                compare(self.stats.get("rest_geometry_aabb_m",{}).get("dimensions",[]),c["dimensions_m"],tolerance,"DIMENSION_MISMATCH","rest AABB")
            else:self.issue("PHYSICAL_DIMENSIONS_UNVERIFIED","no declared dimensions","unknown")
            named={}
            for i,n in enumerate(nodes):named.setdefault(n.get("name"),[]).append(i)
            def named_node(name):
                matches=named.get(name,[]);require(len(matches)==1 and matches[0] in worlds,"missing or ambiguous active node: "+name);return matches[0]
            for name,expected in sorted(c.get("pivots_local_m",{}).items()):
                compare(list(matrix(nodes[named_node(name)])[12:15]),expected,tolerance,"PIVOT_MISMATCH",name)
            if not c.get("pivots_local_m"):self.issue("PIVOT_INTENT_UNVERIFIED","no declared local pivots","unknown")
            if "forward" in c:
                direction=c["forward"];m=worlds[named_node(direction["node"])]
                axis=direction["local_axis"];require(len(axis)==3 and finite(axis) and abs(length(axis)-1)<1e-6,"invalid forward axis")
                v=sub(point(m,axis),point(m,(0,0,0)));require(length(v)>1e-12,"collapsed forward axis")
                compare([x/length(v) for x in v],direction["world_axis"],.001,"ORIENTATION_MISMATCH","declared forward")
            else:self.issue("ORIENTATION_UNVERIFIED","no declared directional fiducial","unknown")
            self.stats["contract_checked"]=True
        else:
            self.issue("PHYSICAL_DIMENSIONS_OR_FORWARD_UNVERIFIED","requires declared per-asset dimensions/orientation and Godot comparison","unknown")
            self.issue("PIVOT_INTENT_UNVERIFIED","finite local transforms checked; semantic pivot intent needs source contract","unknown")
        if self.category in BUDGETS:
            b=BUDGETS[self.category]
            self.stats["provisional_file_budget"]={"category":self.category,"triangles_lod0":b.triangles[0],"material_slots":b.max_material_slots,"scope":"individual exported file, not assembled asset","hardware_validated":False}
            for key,limit in (("triangles",b.triangles[0]),("material_slots",b.max_material_slots)):
                if self.stats[key]>limit:self.conditional("PROVISIONAL_BUDGET",f"{key} {self.stats[key]} > {limit}")
        else:self.issue("BUDGET_UNASSIGNED",str(self.category),"unknown")
    def trace(self):
        trace=self.doc.get("asset",{}).get("extras",{}).get("frontline")
        if not trace:
            self.issue("SOURCE_TRACE_MISSING","legacy or third-party file","error" if self.strict else "unknown");return
        source=trace["source"];require(bool(source["revision"]) and bool(source["files"]),"empty source trace")
        paths=set()
        for f in source["files"]:
            p=f["path"];require(p not in paths,"duplicate source trace");paths.add(p)
            require(re.fullmatch("[0-9a-f]{64}",f["sha256"]) is not None,"invalid source SHA256")
            require(digest(safe(self.source_root,p).read_bytes())==f["sha256"],"source digest mismatch: "+p)
        self.stats["source_revision"]=source["revision"]
    def run(self):
        try:
            self.doc,bin_chunk=parse_file(safe(self.root,self.path));d=self.doc
            require(d["asset"]["version"]=="2.0","not glTF 2.0")
            self.buffers=[]
            for i,b in enumerate(d.get("buffers",[])):
                data=self.uri(b["uri"]) if "uri" in b else bin_chunk
                require(data is not None and type(b["byteLength"]) is int and b["byteLength"]>0 and b["byteLength"]<=len(data),"invalid buffer length")
                self.buffers.append(data[:b["byteLength"]])
            for i in range(len(d.get("bufferViews",[]))):self.view(i)
            for i in range(len(d.get("accessors",[]))):
                try:self.values(i)
                except NotImplementedError as e:self.issue("ACCESSOR_UNSUPPORTED",f"{i}: {e}","unknown")
            metrics=self.geometry();self.materials();self.hierarchy(metrics);self.trace()
            if d.get("extensionsRequired"):self.issue("EXTENSIONS_UNVERIFIED",d["extensionsRequired"],"unknown")
            if self.strict and any(x["code"]=="ACCESSOR_UNSUPPORTED" for x in self.unknown):self.issue("STRICT_UNSUPPORTED","unsupported accessor")
        except (OSError,ValueError,KeyError,IndexError,TypeError,AttributeError,OverflowError,RecursionError,struct.error) as e:self.issue("INVALID_DOCUMENT",str(e))
        try: checksum=digest(safe(self.root,self.path).read_bytes())
        except (ValueError,OSError): checksum=None
        return {"path":self.path,"category":self.category,"sha256":checksum,"metrics":self.stats,"errors":self.errors,"warnings":self.warnings,"unknown":self.unknown,"technical_status":"fail" if self.errors else "warning" if self.warnings else "pass_with_unknowns" if self.unknown else "pass","visual_approval":False}
def report(root,strict=False,source_root=None):
    root=Path(root).resolve();catalog=build(root)
    owners={o["path"]:a["category"] for a in catalog["assets"] for o in a["outputs"]}
    paths=sorted(p for p,r in catalog["resources"].items() if r["status"]!="missing" and Path(p).suffix.lower() in (".glb",".gltf"))
    rows=[Audit(root,p,owners.get(p),strict,source_root).run() for p in paths]
    return {"schema_version":1,"revision":catalog["revision"],"scope":"original_gltf_files","files":rows,"counts":dict(Counter(r["technical_status"] for r in rows)),"missing_catalog_references":catalog["missing_literal_references"],"dynamic_references":catalog["dynamic_references"],"visual_approval":False}
def main():
    p=argparse.ArgumentParser();p.add_argument("--root",default=".");p.add_argument("--output",required=True);p.add_argument("--file",action="append");p.add_argument("--strict",action="store_true");p.add_argument("--source-root");p.add_argument("--category",default="object");p.add_argument("--audit-only",action="store_true");p.add_argument("--contract")
    a=p.parse_args()
    if a.file:
        contract=json.loads(Path(a.contract).read_text()) if a.contract else None
        rows=[Audit(a.root,f,a.category,a.strict,a.source_root,contract).run() for f in sorted(a.file)]
        result={"schema_version":1,"files":rows,"counts":dict(Counter(r["technical_status"] for r in rows)),"visual_approval":False}
    else:result=report(a.root,a.strict,a.source_root)
    Path(a.output).parent.mkdir(parents=True,exist_ok=True);Path(a.output).write_bytes(canonical(result))
    print("ASSET_VALIDATION_REPORT",json.dumps(result["counts"],sort_keys=True))
    failed=any(r["errors"] for r in result["files"]) or bool(result.get("missing_catalog_references"))
    return 1 if failed and not a.audit_only else 0
if __name__=="__main__":raise SystemExit(main())
