"""QA-only authored finishing profiles and material variants."""
from dataclasses import replace
from .organic import CustomTopology
from .recipes import PythonBackend
from .pbr import MaterialLibrary,generate_library

# The beveled silhouette is authored geometry, not a renderer effect.
def bevel_block(id,size,level):
    x,y,z=size;rx,rz=x/2,z/2
    d=min(rx,rz)*.18;b=min(x,y,z)*.08
    rings=((0,b),(b,0),(y-b,0),(y,b)) if level==0 else ((0,0),(y,0))
    verts=[]
    for h,inset in rings:
        a,c=rx-inset,rz-inset;k=min(d,a*.4,c*.4)
        verts.extend((u,h,v) for u,v in ((-a+k,-c),(a-k,-c),(a,-c+k),(a,c-k),(a-k,c),(-a+k,c),(-a,c-k),(-a,-c+k)))
    faces=[]
    for j in range(len(rings)-1):
        for i in range(8):
            n=(i+1)%8;l=j*8;u=l+8
            faces.append((l+i,u+i,u+n,l+n))
    top=(len(rings)-1)*8
    for i in range(1,7):
        faces.append((0,i,i+1));faces.append((top,top+i+1,top+i))
    return PythonBackend().build(CustomTopology(id,tuple(verts),tuple(faces),True))

# New local colors use the original PBR roughness/normal maps and deterministic RGB.
VARIANTS={
    "safety_amber":("painted_steel",(221,153,36)),
    "graphite":("rubber",(48,52,58)),
    "olive_textile":("fabric",(76,86,54)),
    "sand_textile":("fabric",(139,123,87)),
    "foliage":("fabric",(61,102,46)),
    "earth":("concrete",(112,92,69)),
    "cool_steel":("painted_steel",(75,96,111)),
    "signal_blue":("painted_steel",(42,103,163)),
    "signal_lime":("painted_steel",(130,174,61)),
}
def finished_library(size=128,seed=9133):
    lib=generate_library(size,seed);textures=list(lib.textures);materials=list(lib.materials)
    byid={t.id:t for t in textures}
    for name,(parent,color) in sorted(VARIANTS.items()):
        original=lib.material(parent);t=byid[original.base_color_texture]
        pixels=bytearray()
        for i in range(0,len(t.rgb),3):
            # retain texture detail; modest physically plausible contrast.
            luminance=sum(t.rgb[i:i+3])/3
            factor=.96+.08*luminance/255 if parent=='painted_steel' else .88+.24*luminance/255
            pixels.extend(max(0,min(255,round(v*factor))) for v in color)
        tex=replace(t,id=name+"_base_color",rgb=bytes(pixels),source="procedural:pilot-finish-v1:"+name)
        textures.append(tex);materials.append(replace(original,id=name,base_color_texture=tex.id,normal_scale=.28 if parent=="painted_steel" else .65))
    return MaterialLibrary(materials,textures)
