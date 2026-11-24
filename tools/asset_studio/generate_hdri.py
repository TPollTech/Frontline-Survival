"""Original synthetic equirectangular Radiance RGBE studio light, not a photograph."""
import math
import hashlib
import json
from pathlib import Path

def rgbe(rgb):
    peak=max(rgb)
    if peak<1e-32:return bytes(4)
    mantissa,exponent=math.frexp(peak)
    scale=mantissa*256/peak
    return bytes([min(255,int(v*scale)) for v in rgb]+[exponent+128])

def generate(width=256,height=128):
    if width!=2*height or not 8<=width<=2048:raise ValueError("invalid panorama")
    header=f"#?RADIANCE\n# Frontline synthetic studio v1\nFORMAT=32-bit_rle_rgbe\n\n-Y {height} +X {width}\n".encode()
    out=bytearray(header)
    # Smooth spherical softboxes in linear light; broad neutral fill.
    lights=[((.58,.72,.38),(.99,.94,.86),9.,.075),
            ((-.8,.5,.25),(.78,.87,1.),4.,.12),
            ((.05,.6,-.8),(1.,1.,1.),6.,.055)]
    lights=[(tuple(v/math.sqrt(sum(t*t for t in pos)) for v in pos),rgb,power,spread) for pos,rgb,power,spread in lights]
    for y in range(height):
        theta=math.pi*(y+.5)/height
        row=[]
        for x in range(width):
            phi=2*math.pi*(x+.5)/width
            d=(math.sin(theta)*math.cos(phi),math.cos(theta),math.sin(theta)*math.sin(phi))
            rgb=[.12+.22*max(0,d[1])]*3
            for pos,col,power,spread in lights:
                k=power*math.exp((sum(a*b for a,b in zip(d,pos))-1)/spread)
                rgb=[v+k*c for v,c in zip(rgb,col)]
            row.append(rgbe(rgb))
        out.extend((2,2,width>>8,width&255))
        for channel in range(4):
            for start in range(0,width,128):
                block=bytes(p[channel] for p in row[start:start+128])
                out.append(len(block));out.extend(block)
    return bytes(out)

def write(directory):
    p=Path(directory)
    data=generate()
    (p/"studio-light.hdr").write_bytes(data)
    metadata={"kind":"synthetic_radiance_rgbe","source":"tools/asset_studio/generate_hdri.py","width":256,"height":128,"sha256":hashlib.sha256(data).hexdigest(),"photographic":False}
    (p/"studio-light.json").write_text(json.dumps(metadata,sort_keys=True)+"\n",encoding="utf-8")
