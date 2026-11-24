"""Immutable PBR material library and reproducible, original procedural textures.

Canonical colors in material factors are linear; color texture bytes are sRGB.
ORM = occlusion R, roughness G, metallic B. Normal maps are tangent-space +Y.
No modification of legacy assets; generated output is explicit.
"""
from dataclasses import dataclass, asdict
from pathlib import Path
import hashlib
import json
import math
import struct
import zlib
from .model import MaterialSpec, number, vector, stable_id, require

ROLES={"base_color":"sRGB","emissive":"sRGB","normal":"linear","orm":"linear"}

def _sha(data):
    return hashlib.sha256(data).hexdigest()

def _json(data):
    return json.dumps(data,sort_keys=True,separators=(",",":"),allow_nan=False)

def _chunk(kind,data):
    return struct.pack(">I",len(data))+kind+data+struct.pack(">I",zlib.crc32(kind+data)&0xffffffff)

def _png(w,h,rgb):
    """Canonical RGB8 PNG, filter 0, deterministic uncompressed DEFLATE blocks."""
    stride=w*3
    raw=b"".join(b"\0"+rgb[y*stride:(y+1)*stride] for y in range(h))
    # Stored blocks avoid compression-library-version-dependent encodings.
    data=bytearray(b"\x78\x01")
    for i in range(0,len(raw),65535):
        block=raw[i:i+65535]
        data.append(int(i+len(block)==len(raw)))
        data.extend(struct.pack("<HH",len(block),65535-len(block)))
        data.extend(block)
    data.extend(struct.pack(">I",zlib.adler32(raw)&0xffffffff))
    return b"\x89PNG\r\n\x1a\n"+_chunk(b"IHDR",struct.pack(">IIBBBBB",w,h,8,2,0,0,0))+_chunk(b"IDAT",bytes(data))+_chunk(b"IEND",b"")

def _safe_name(id):
    stable_id(id)
    require(":" not in id,"texture ID cannot contain colon")
    return id+".png"

@dataclass(frozen=True)
class TextureData:
    id: str
    role: str
    width: int
    height: int
    rgb: bytes
    source: str
    license: str

    def __post_init__(self):
        _safe_name(self.id)
        require(self.role in ROLES,"unknown texture role")
        require(all(type(n) is int and 1<=n<=2048 for n in (self.width,self.height)),"invalid texture dimensions")
        require(type(self.rgb) is bytes and len(self.rgb)==self.width*self.height*3,"invalid RGB8 buffer")
        require(all(isinstance(v,str) and bool(v.strip()) for v in (self.source,self.license)),"missing source/license")
        if self.role=="normal":
            for i in range(0,len(self.rgb),3):
                x,y,z=(2*c/255-1 for c in self.rgb[i:i+3])
                require(z>=0 and abs(x*x+y*y+z*z-1)<0.025,"invalid +Y tangent normal texel")

    @property
    def color_space(self):
        return ROLES[self.role]

    def png(self):
        return _png(self.width,self.height,self.rgb)

    def metadata(self):
        return {"id":self.id,"role":self.role,"color_space":self.color_space,
                "width":self.width,"height":self.height,"format":"RGB8_PNG",
                "path":_safe_name(self.id),"sha256":_sha(self.png()),
                "pixel_sha256":_sha(self.rgb),"source":self.source,"license":self.license}

@dataclass(frozen=True)
class PBRMaterial(MaterialSpec):
    base_color_texture: str | None=None
    orm_texture: str | None=None
    normal_texture: str | None=None
    emissive_texture: str | None=None
    emissive: tuple=(0.,0.,0.)
    normal_scale: float=1.
    occlusion_strength: float=1.
    alpha_mode: str="OPAQUE"
    alpha_cutoff: float=0.5
    double_sided: bool=False

    def __post_init__(self):
        super().__post_init__()
        for value in (self.base_color_texture,self.orm_texture,self.normal_texture,self.emissive_texture):
            if value is not None:
                _safe_name(value)
        e=vector(self.emissive,3)
        n,o,a=map(number,(self.normal_scale,self.occlusion_strength,self.alpha_cutoff))
        require(all(0<=x<=1 for x in e) and n>=0 and 0<=o<=1 and 0<=a<=1,"invalid PBR factors")
        require(self.alpha_mode in ("OPAQUE","MASK","BLEND") and type(self.double_sided) is bool,"invalid render mode")
        for key,value in (("emissive",e),("normal_scale",n),("occlusion_strength",o),("alpha_cutoff",a)):
            object.__setattr__(self,key,value)

    def texture_slots(self):
        return {role:id for role,id in (("base_color",self.base_color_texture),("orm",self.orm_texture),
                 ("normal",self.normal_texture),("emissive",self.emissive_texture)) if id is not None}

@dataclass(frozen=True)
class MaterialLibrary:
    materials: tuple
    textures: tuple

    def __post_init__(self):
        for key,cls in (("materials",PBRMaterial),("textures",TextureData)):
            items=tuple(getattr(self,key))
            require(all(isinstance(x,cls) for x in items),"invalid library entry")
            require(len({x.id for x in items})==len(items),"duplicate library ID")
            object.__setattr__(self,key,tuple(sorted(items,key=lambda x:x.id)))
        byid={x.id:x for x in self.textures}
        for m in self.materials:
            for role,id in m.texture_slots().items():
                require(id in byid and byid[id].role==role,"missing texture or role mismatch")

    def material(self,id):
        for m in self.materials:
            if m.id==id:
                return m
        raise KeyError(id)

    def manifest(self):
        return {"schema_version":1,"workflow":"metallic_roughness","normal_convention":"+Y",
                "orm_channels":{"R":"occlusion","G":"roughness","B":"metallic"},
                "materials":[asdict(m) for m in self.materials],
                "textures":[t.metadata() for t in self.textures]}

    def canonical_json(self):
        return _json(self.manifest())

    def sha256(self):
        return _sha(self.canonical_json().encode("utf-8"))

    def write(self,directory):
        """Write only into an empty directory; never overwrite existing assets."""
        p=Path(directory)
        p.mkdir(parents=True,exist_ok=True)
        require(not any(p.iterdir()),"material output directory must be empty")
        for t in self.textures:
            (p/_safe_name(t.id)).write_bytes(t.png())
        (p/"materials.json").write_text(self.canonical_json()+"\n",encoding="utf-8")

    def verify(self,directory):
        p=Path(directory)
        require(_json(json.loads((p/"materials.json").read_text(encoding="utf-8")))==self.canonical_json(),"material manifest mismatch")
        expected={"materials.json",*(_safe_name(t.id) for t in self.textures)}
        require({x.name for x in p.iterdir()}==expected,"unexpected or missing material file")
        for t in self.textures:
            require(_sha((p/_safe_name(t.id)).read_bytes())==t.metadata()["sha256"],"texture hash mismatch: "+t.id)
        return True

# sRGB colors, linear roughness/metallic, relief and texture pattern.
PRESETS={
    "brushed_metal":((155,162,168),0.38,1.,0.13,"grain"),
    "painted_steel":((66,81,73),0.55,0.,0.10,"noise"),
    "rubber":((42,44,46),0.83,0.,0.20,"noise"),
    "concrete":((144,139,130),0.88,0.,0.34,"stone"),
    "wood":((137,91,53),0.68,0.,0.20,"grain"),
    "fabric":((99,109,84),0.91,0.,0.21,"weave"),
}

def _noise(x,y,seed):
    # Integer mixer, no ambient RNG state.
    v=(x*374761393+y*668265263+seed*2246822519)&0xffffffff
    v=((v^(v>>13))*1274126177)&0xffffffff
    return ((v^(v>>16))&65535)/65535

def _byte(x):
    return max(0,min(255,int(x+0.5)))

def _height(pattern,x,y,n,seed):
    x,y=x%n,y%n
    a=_noise(x,y,seed)
    u,v=math.tau*x/n,math.tau*y/n
    if pattern=="grain":
        return 0.7*(0.5+0.5*math.sin(8*u+0.5*math.sin(2*v)))+0.3*a
    if pattern=="weave":
        return 0.4+0.2*math.sin(8*u)+0.2*math.sin(8*v)+0.2*a
    if pattern=="stone":
        return 0.6*a+0.2*(1+math.sin(3*u)*math.cos(4*v))
    return a

def generate_library(size=128,seed=9133):
    require(type(size) is int and size in (32,64,128,256,512),"unsupported texture size")
    require(type(seed) is int and 0<=seed<=0xffffffff,"invalid seed")
    materials,textures=[],[]
    for i,(name,(color,rough,metal,relief,pattern)) in enumerate(sorted(PRESETS.items())):
        base,orm,normal=bytearray(),bytearray(),bytearray()
        s=seed+i
        heights=[_height(pattern,x,y,size,s) for y in range(size) for x in range(size)]
        def at(x,y):
            return heights[(y%size)*size+(x%size)]
        for y in range(size):
            for x in range(size):
                h=at(x,y)
                variation=0.86+0.28*h
                base.extend(_byte(c*variation) for c in color)
                orm.extend((255,_byte(255*(rough+0.12*(h-0.5))),_byte(255*metal)))
                # Image rows run down; tangent +V runs up in this source convention.
                nx=-relief*(at(x+1,y)-at(x-1,y))
                ny=relief*(at(x,y+1)-at(x,y-1))
                d=math.sqrt(nx*nx+ny*ny+1)
                normal.extend(_byte(255*(v/d*0.5+0.5)) for v in (nx,ny,1.))
        ids={}
        for role,data in (("base_color",base),("orm",orm),("normal",normal)):
            tid=name+"_"+role
            ids[role]=tid
            textures.append(TextureData(tid,role,size,size,bytes(data),
                f"procedural:pbr-v1:{name}:size={size}:seed={s}","CC0-1.0"))
        # Texture channels carry absolute factors, not a second multiplication.
        materials.append(PBRMaterial(name,(1,1,1,1),1.,1.,
            base_color_texture=ids["base_color"],orm_texture=ids["orm"],normal_texture=ids["normal"]))
    return MaterialLibrary(materials,textures)
