"""Optional isolated Blender process; no bpy import in normal Python."""
from __future__ import annotations
import json
import math
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
from .model import MeshSpec, number, require, stable_id, Transform
from .recipes import PythonBackend
from .coplanar import simplify_coplanar_solid

class BlenderError(RuntimeError):
    pass

class BlenderBackend:
    def __init__(self, executable=None, timeout=120):
        self.executable=executable or os.environ.get("FRONTLINE_BLENDER") or shutil.which("blender")
        self.timeout=number(timeout)
        require(self.timeout>0,"timeout must be positive")

    @property
    def available(self):
        return bool(self.executable and shutil.which(self.executable))

    def build(self, recipe):
        return self.evaluate(PythonBackend().build(recipe))

    def evaluate(self, mesh: MeshSpec, *, bevel_m=0., segments=1):
        """Real Blender mesh evaluation; optional angle-limited bevel for technical fixtures.
        Operates on local geometry, not scene hierarchy or material slots.
        """
        require(isinstance(mesh,MeshSpec),"expected MeshSpec")
        bevel=number(bevel_m)
        require(bevel>=0 and type(segments) is int and 1<=segments<=8,"invalid bevel parameters")
        if bevel>0:
            require(mesh.closed_oriented() and mesh.signed_volume()>0,"bevel requires closed outward input")
        return self._evaluate(mesh, {"bevel_m":bevel,"segments":segments})

    def bevel(self, mesh, width_m, segments=3, *, angle_rad=math.pi/6):
        require(isinstance(mesh,MeshSpec),"expected MeshSpec")
        width,angle=number(width_m),number(angle_rad)
        require(width>0 and 0<angle<math.pi and type(segments) is int and 1<=segments<=8,"invalid bevel")
        require(mesh.closed_oriented() and mesh.signed_volume()>0,"bevel requires closed outward input")
        return self._evaluate(mesh, {"bevel_m":width,"segments":segments,"angle_rad":angle})

    def boolean(self, id, left, right, operation, *, right_transform=None):
        """Real Blender exact CSG; empty/invalid results raise BlenderError."""
        stable_id(id)
        require(operation in ("union","difference","intersection"),"unsupported boolean")
        require(all(isinstance(m,MeshSpec) and m.closed_oriented() and m.signed_volume()>0 for m in (left,right)),
                "boolean requires closed outward operands")
        t=Transform() if right_transform is None else right_transform
        require(isinstance(t,Transform),"expected transform")
        operand=MeshSpec(right.id,[t.point(v) for v in right.vertices],right.triangles)
        return self._evaluate(MeshSpec(id,left.vertices,left.triangles),
            {"bevel_m":0.,"segments":1,"boolean":{"operation":operation,
             "vertices":operand.vertices,"triangles":operand.triangles}})

    def _evaluate(self, mesh, options):
        if not self.available:
            raise BlenderError("Blender unavailable; set FRONTLINE_BLENDER or install blender")
        with tempfile.TemporaryDirectory(prefix="frontline-blender-") as temp:
            src,dst=Path(temp)/"input.json",Path(temp)/"output.json"
            src.write_text(json.dumps({"id":mesh.id,"vertices":mesh.vertices,"triangles":mesh.triangles,
                                       **options},allow_nan=False),encoding="utf-8")
            bridge=Path(__file__).with_name("blender_bridge.py").resolve()
            try:
                proc=subprocess.run([self.executable,"--background","--factory-startup","--disable-autoexec",
                    "--python-exit-code","1","--python",str(bridge),"--",str(src),str(dst)],
                    capture_output=True,text=True,timeout=self.timeout,check=False)
            except (OSError,subprocess.TimeoutExpired) as exc:
                raise BlenderError(f"Blender process failed: {exc}") from exc
            if proc.returncode!=0 or not dst.is_file():
                raise BlenderError(f"Blender evaluation failed ({proc.returncode}): {(proc.stdout+proc.stderr)[-4000:]}")
            try:
                out=json.loads(dst.read_text(encoding="utf-8"))
                require(out["id"]==mesh.id and bool(out["blender_version"]),"wrong Blender output")
                if "boolean" in options:
                    require(bool(out["vertices"]) and bool(out["triangles"]),"empty boolean result")
                try:
                    result=MeshSpec(out["id"],out["vertices"],out["triangles"])
                except ValueError as exc:
                    if "boolean" not in options:
                        raise
                    # Capture diagnostic geometry rather than losing the failing mesh
                    # when the isolated process temporary directory is removed.
                    bad=[]
                    for face in out["triangles"]:
                        a,b,c=(out["vertices"][i] for i in face)
                        u=[b[i]-a[i] for i in range(3)]
                        v=[c[i]-a[i] for i in range(3)]
                        n=[u[(i+1)%3]*v[(i+2)%3]-u[(i+2)%3]*v[(i+1)%3] for i in range(3)]
                        if sum(x*x for x in n)<=1e-24:
                            bad.append({"indices":face,"points":[a,b,c]})
                            if len(bad)==3:
                                break
                    raise ValueError(f"{exc}; CSG normalization={out.get('csg_normalization')}; degenerate={bad}") from exc
                if mesh.closed_oriented():
                    require(result.closed_oriented() and result.signed_volume()>0,"Blender changed closed orientation")
                if "boolean" in options:
                    result=simplify_coplanar_solid(result)
                return result
            except (ValueError,KeyError,TypeError) as exc:
                raise BlenderError(f"invalid Blender result: {exc}") from exc
