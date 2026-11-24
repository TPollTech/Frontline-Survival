"""Material factors, deterministic PNGs, provenance, and actual Blender decoding."""
import json
import os
from pathlib import Path
import struct
import subprocess
import tempfile
import unittest
import zlib
from tools.asset_pipeline.parametric import Box, PythonBackend, SceneSpec, NodeSpec, BlenderBackend
from tools.asset_pipeline.parametric.pbr import TextureData, PBRMaterial, MaterialLibrary, generate_library

class MaterialTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.lib=generate_library(32)

    def test_presets_and_roles(self):
        self.assertEqual(len(self.lib.materials),6)
        self.assertEqual(len(self.lib.textures),18)
        for m in self.lib.materials:
            self.assertEqual(set(m.texture_slots()),{"base_color","orm","normal"})
            self.assertEqual((m.metallic,m.roughness),(1.,1.))

    def test_determinism(self):
        other=generate_library(32)
        self.assertEqual(self.lib.sha256(),other.sha256())
        self.assertEqual(self.lib.textures,other.textures)
        self.assertNotEqual(self.lib.sha256(),generate_library(32,seed=2).sha256())

    def test_color_spaces(self):
        for t in self.lib.textures:
            self.assertEqual(t.color_space,"sRGB" if t.role=="base_color" else "linear")
            self.assertTrue(t.source.startswith("procedural:pbr-v1:"))
            self.assertEqual(t.license,"CC0-1.0")

    def test_png_crc_and_pixel_roundtrip(self):
        for t in self.lib.textures:
            data=t.png()
            self.assertEqual(data[:8],b"\x89PNG\r\n\x1a\n")
            offset=8
            compressed=[]
            while offset<len(data):
                length=struct.unpack(">I",data[offset:offset+4])[0]
                kind=data[offset+4:offset+8]
                payload=data[offset+8:offset+8+length]
                crc=struct.unpack(">I",data[offset+8+length:offset+12+length])[0]
                self.assertEqual(crc,zlib.crc32(kind+payload)&0xffffffff)
                if kind==b"IDAT":
                    compressed.append(payload)
                offset+=length+12
            raw=zlib.decompress(b"".join(compressed))
            stride=t.width*3+1
            self.assertEqual(len(raw),stride*t.height)
            self.assertTrue(all(raw[y*stride]==0 for y in range(t.height)))
            self.assertEqual(b"".join(raw[y*stride+1:(y+1)*stride] for y in range(t.height)),t.rgb)

    def test_orm_values(self):
        for t in self.lib.textures:
            if t.role=="orm":
                self.assertEqual(set(t.rgb[0::3]),{255})
                self.assertEqual(set(t.rgb[2::3]),{255 if t.id=="brushed_metal_orm" else 0})
                self.assertGreater(len(set(t.rgb[1::3])),1)

    def test_normal_variation(self):
        for t in self.lib.textures:
            if t.role=="normal":
                self.assertGreater(len(set(t.rgb[0::3])),1)
                self.assertTrue(all(z>127 for z in t.rgb[2::3]))

    def test_material_validation(self):
        for kw in ({"roughness":1.1},{"normal_scale":-1},{"emissive":(0,1,2)},{"alpha_mode":"BAD"},{"base_color_texture":"../bad"}):
            with self.assertRaises(ValueError):
                PBRMaterial("bad",**kw)

    def test_texture_validation(self):
        for args in (("bad","orm",1,1,b"xx","source","CC0"),("bad","normal",1,1,b"\x00\x00\x00","source","CC0"),("bad","base_color",1,1,b"abc","","CC0")):
            with self.assertRaises(ValueError):
                TextureData(*args)

    def test_library_references(self):
        tex=self.lib.textures[0]
        with self.assertRaises(ValueError):
            MaterialLibrary((PBRMaterial("bad",normal_texture="unknown"),),())
        with self.assertRaises(ValueError):
            MaterialLibrary((PBRMaterial("bad",normal_texture="brushed_metal_base_color"),),self.lib.textures)
        with self.assertRaises(ValueError):
            MaterialLibrary((),(tex,tex))

    def test_scene_material_compatibility(self):
        m=self.lib.material("rubber")
        mesh=PythonBackend().build(Box("box",(1,2,3)))
        s=SceneSpec("fixture",(mesh,),(m,),(NodeSpec("part",mesh.id,material_id=m.id),))
        self.assertEqual(json.loads(s.canonical_json())["scene"]["materials"][0]["normal_texture"],m.normal_texture)

    def test_output_hashes_and_no_overwrite(self):
        with tempfile.TemporaryDirectory() as d:
            self.lib.write(d)
            self.assertTrue(self.lib.verify(d))
            with self.assertRaises(ValueError):
                self.lib.write(d)
            t=self.lib.textures[0]
            p=Path(d)/(t.id+".png")
            p.write_bytes(b"corrupted")
            with self.assertRaises(ValueError):
                self.lib.verify(d)

    def test_invalid_generation(self):
        for size,seed in ((31,1),(True,1),(32,-1),(32,True)):
            with self.assertRaises(ValueError):
                generate_library(size,seed)

class BlenderMaterialTests(unittest.TestCase):
    def test_real_decode_and_shader_links(self):
        b=BlenderBackend()
        if not b.available:
            if os.environ.get("FRONTLINE_REQUIRE_BLENDER")=="1":
                self.fail("actual Blender required")
            self.skipTest("optional Blender absent")
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)
            lib=generate_library(32)
            lib.write(root/"library")
            out=root/"evidence.json"
            script=Path(__file__).resolve().parents[1]/"tools/asset_pipeline/parametric/pbr_bridge.py"
            run=subprocess.run([b.executable,"--background","--factory-startup","--disable-autoexec","--python-exit-code","1","--python",str(script),"--",str(root/"library"),str(out)],capture_output=True,text=True,timeout=120)
            self.assertEqual(run.returncode,0,msg=run.stdout+run.stderr)
            evidence=json.loads(out.read_text())
            self.assertEqual(evidence["decoded_images"],18)
            self.assertEqual(len(evidence["materials"]),6)
            self.assertTrue(all(len(m["linked"])==4 for m in evidence["materials"]))

if __name__=="__main__":
    unittest.main()
