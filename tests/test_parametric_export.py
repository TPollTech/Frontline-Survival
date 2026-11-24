import base64
import json
from pathlib import Path
import struct
import tempfile
import unittest
from dataclasses import replace
from tools.asset_pipeline.parametric.export_fixture import fixture
from tools.asset_pipeline.parametric.exporter import export_bundle,source_manifest,write_bundle,verify_bundle,digest
from tools.asset_pipeline.parametric import Transform

def unpack(files):
    glb=files["asset.glb"]
    magic,v,n=struct.unpack_from("<4sII",glb)
    assert (magic,v,n)==(b"glTF",2,len(glb))
    size,kind=struct.unpack_from("<I4s",glb,12)
    assert kind==b"JSON" and size%4==0
    d=json.loads(glb[20:20+size])
    off=20+size
    length,kind=struct.unpack_from("<I4s",glb,off)
    assert kind==b"BIN\0" and off+8+length==len(glb)
    return d,glb[off+8:]

def values(d,b,i):
    a=d["accessors"][i]
    view=d["bufferViews"][a["bufferView"]]
    n={"SCALAR":1,"VEC2":2,"VEC3":3,"VEC4":4,"MAT4":16}[a["type"]]
    f={5126:"f",5123:"H",5125:"I"}[a["componentType"]]
    return list(struct.iter_unpack("<"+f*n,b[view["byteOffset"]:view["byteOffset"]+view["byteLength"]]))

class ExportTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.scene,cls.renders,cls.lib,cls.rig=fixture()
        cls.sources={"revision":"fixture-v1","files":[{"path":"fixture.py","sha256":"0"*64}]}
        cls.files=export_bundle(cls.scene,cls.renders,cls.lib,sources=cls.sources,rig=cls.rig)

    def test_determinism(self):
        self.assertEqual(self.files,export_bundle(self.scene,self.renders,self.lib,sources=self.sources,rig=self.rig))
        d=json.loads(self.files["export.json"])
        for name,info in d["outputs"].items():
            self.assertEqual(info["sha256"],digest(self.files[name]))

    def test_gltf_glb_equivalence(self):
        d,b=unpack(self.files)
        g=json.loads(self.files["asset.gltf"])
        uri=g["buffers"][0].pop("uri")
        self.assertEqual(base64.b64decode(uri.split(",")[1]),b)
        self.assertEqual(d,g)
        self.assertEqual(d["buffers"][0]["byteLength"],len(b))
        for v in d["bufferViews"]:
            self.assertEqual(v["byteOffset"]%4,0)
            self.assertLessEqual(v["byteOffset"]+v["byteLength"],len(b))

    def test_geometry_and_uv(self):
        d,b=unpack(self.files)
        p=d["meshes"][0]["primitives"][0]
        a=p["attributes"]
        r=self.renders[0]
        self.assertEqual(values(d,b,a["POSITION"]),list(r.positions))
        self.assertEqual(values(d,b,a["TEXCOORD_0"]),[(u,1-v) for u,v in r.uv])
        self.assertEqual(values(d,b,a["TANGENT"]),[(*t[:3],-t[3]) for t in r.tangents])
        self.assertEqual(values(d,b,p["indices"]),[(i,) for i in r.indices])

    def test_skin_and_hierarchy(self):
        d,b=unpack(self.files)
        s=d["skins"][0]
        self.assertEqual([d["nodes"][i]["name"] for i in s["joints"]],["bone:root","bone:tip"])
        self.assertEqual(values(d,b,s["inverseBindMatrices"]),[self.rig.skeleton.inverse_bind()[x].matrix for x in ("root","tip")])
        node=next(n for n in d["nodes"] if n["name"]=="panel")
        self.assertEqual(node["skin"],0)
        a=d["meshes"][node["mesh"]]["primitives"][0]["attributes"]
        self.assertEqual([sum(row) for row in values(d,b,a["WEIGHTS_0"])],[1.]*4)
        self.assertTrue(any(n["name"]=="socket:tip_socket" for n in d["nodes"]))

    def test_material_and_images(self):
        d,b=unpack(self.files)
        m=d["materials"][0]
        self.assertEqual(m["occlusionTexture"]["index"],m["pbrMetallicRoughness"]["metallicRoughnessTexture"]["index"])
        self.assertEqual(len(d["images"]),3)
        for i in d["images"]:
            v=d["bufferViews"][i["bufferView"]]
            png=b[v["byteOffset"]:v["byteOffset"]+v["byteLength"]]
            self.assertEqual(png[:8],b"\x89PNG\r\n\x1a\n")
            self.assertEqual(digest(png),i["extras"]["export_sha256"])

    def test_normal_green_flip(self):
        from tools.asset_pipeline.parametric.pbr import _png
        d,b=unpack(self.files)
        i=next(i for i in d["images"] if i["extras"]["role"]=="normal")
        t=next(t for t in self.lib.textures if t.id==i["name"])
        rgb=bytearray(t.rgb)
        for k in range(1,len(rgb),3):
            rgb[k]=255-rgb[k]
        v=d["bufferViews"][i["bufferView"]]
        self.assertEqual(b[v["byteOffset"]:v["byteOffset"]+v["byteLength"]],_png(t.width,t.height,bytes(rgb)))

    def test_sources(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/"source.py"
            p.write_bytes(b"abc")
            a=source_manifest(d,["source.py"],"rev")
            self.assertEqual(a["files"][0]["sha256"],digest(b"abc"))
            p.write_bytes(b"def")
            self.assertNotEqual(a,source_manifest(d,["source.py"],"rev"))
            with self.assertRaises(ValueError):
                source_manifest(d,["../source.py"],"rev")

    def test_bundle_io(self):
        with tempfile.TemporaryDirectory() as d:
            write_bundle(d,self.files)
            self.assertTrue(verify_bundle(d,self.files))
            with self.assertRaises(ValueError):
                write_bundle(d,self.files)
            (Path(d)/"asset.glb").write_bytes(b"bad")
            with self.assertRaises(ValueError):
                verify_bundle(d,self.files)

    def test_missing_render_and_shear(self):
        with self.assertRaises(ValueError):
            export_bundle(self.scene,(),self.lib,sources=self.sources)
        t=Transform((1,0,0,0,0.5,1,0,0,0,0,1,0,0,0,0,1))
        s=replace(self.scene,nodes=tuple(replace(n,local=t) if n.id=="panel" else n for n in self.scene.nodes))
        with self.assertRaises(ValueError):
            export_bundle(s,self.renders,self.lib,sources=self.sources)

if __name__=="__main__":
    unittest.main()
