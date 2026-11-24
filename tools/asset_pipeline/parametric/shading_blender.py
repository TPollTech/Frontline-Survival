"""Optional real Blender MikkTSpace backend; no bpy import in host Python."""
import json
import subprocess
import tempfile
from pathlib import Path
from .blender_backend import BlenderBackend, BlenderError
from .model import vector, require, dot
from .shading import norm, _frames

def blender_tangents(mesh,normals,uv, *, backend=None):
    backend=BlenderBackend() if backend is None else backend
    require(isinstance(backend,BlenderBackend),"expected BlenderBackend")
    ns=tuple(vector(n,3) for n in normals)
    require(len(ns)==3*len(mesh.triangles) and all(abs(norm(n)-1)<1e-6 for n in ns),"bad normals")
    uv,_=_frames(mesh,uv)
    if not backend.available:
        raise BlenderError("Blender unavailable for MikkTSpace")
    with tempfile.TemporaryDirectory(prefix="frontline-mikk-") as temp:
        src,dst=Path(temp)/"input.json",Path(temp)/"output.json"
        src.write_text(json.dumps({"vertices":mesh.vertices,"triangles":mesh.triangles,"normals":ns,"uv":uv},allow_nan=False),encoding="utf-8")
        script=Path(__file__).with_name("shading_bridge.py").resolve()
        try:
            proc=subprocess.run([backend.executable,"--background","--factory-startup","--disable-autoexec",
                "--python-exit-code","1","--python",str(script),"--",str(src),str(dst)],
                capture_output=True,text=True,timeout=backend.timeout,check=False)
            if proc.returncode or not dst.is_file():
                raise BlenderError(f"MikkTSpace failed: {(proc.stdout+proc.stderr)[-4000:]}")
            data=json.loads(dst.read_text(encoding="utf-8"))
            actual=tuple(vector(n,3) for n in data["normals"])
            ts=tuple(vector(t,4) for t in data["tangents"])
            require(bool(data["version"]) and len(actual)==len(ts)==len(ns),"Mikk corner count")
            for n,a,t in zip(ns,actual,ts):
                # Blender 3.x quantizes custom split normals; reject material drift.
                require(dot(n,a)>0.99999 and abs(norm(t[:3])-1)<1e-5 and t[3] in (-1.,1.),"invalid Blender tangent frame")
                # Orthogonalize against original canonical normal, not quantized one.
            from .shading import unit, scale
            from .model import sub
            return tuple(unit(sub(t[:3],scale(n,dot(n,t[:3]))))+(t[3],) for n,t in zip(ns,ts))
        except (OSError,subprocess.TimeoutExpired,ValueError,KeyError,TypeError) as exc:
            raise BlenderError(f"MikkTSpace evaluation failed: {exc}") from exc
