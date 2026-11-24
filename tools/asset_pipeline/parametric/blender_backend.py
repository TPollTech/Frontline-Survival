"""Optional isolated Blender process; no bpy import in normal Python."""
from __future__ import annotations
import json
import math
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
from .model import MeshSpec, number, require
from .recipes import PythonBackend

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
            require(mesh.closed_oriented(),"bevel requires closed oriented input")
        if not self.available:
            raise BlenderError("Blender unavailable; set FRONTLINE_BLENDER or install blender")
        with tempfile.TemporaryDirectory(prefix="frontline-blender-") as temp:
            src,dst=Path(temp)/"input.json",Path(temp)/"output.json"
            src.write_text(json.dumps({"id":mesh.id,"vertices":mesh.vertices,"triangles":mesh.triangles,
                                       "bevel_m":bevel,"segments":segments},allow_nan=False),encoding="utf-8")
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
                result=MeshSpec(out["id"],out["vertices"],out["triangles"])
                if mesh.closed_oriented():
                    require(result.closed_oriented() and result.signed_volume()>0,"Blender changed closed orientation")
                return result
            except (ValueError,KeyError,TypeError) as exc:
                raise BlenderError(f"invalid Blender result: {exc}") from exc
