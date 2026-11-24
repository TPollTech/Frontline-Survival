import json, struct, tempfile, unittest
from pathlib import Path
from tools.asset_pipeline.validate_gltf import Audit, digest, matrix, point
from tools.asset_pipeline.reconcile_validation import reconcile

class ValidationTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name)
        data=struct.pack("<9f9f6f3H",0,0,0,1,0,0,0,1,0,0,0,1,0,0,1,0,0,1,0,0,1,0,0,1,0,1,2)
        self.root.joinpath("mesh.bin").write_bytes(data)
        self.root.joinpath("source.py").write_text("fixture")
        self.doc={"asset":{"version":"2.0","extras":{"frontline":{"source":{"revision":"fixture","files":[{"path":"source.py","sha256":digest(b"fixture")}]}}}},
            "buffers":[{"uri":"mesh.bin","byteLength":len(data)}],
            "bufferViews":[{"buffer":0,"byteOffset":o,"byteLength":n} for o,n in [(0,36),(36,36),(72,24),(96,6)]],
            "accessors":[{"bufferView":i,"componentType":5126 if i<3 else 5123,"count":3,"type":t} for i,t in enumerate(["VEC3","VEC3","VEC2","SCALAR"])],
            "materials":[{"pbrMetallicRoughness":{"metallicFactor":.1,"roughnessFactor":.7}}],
            "meshes":[{"primitives":[{"attributes":{"POSITION":0,"NORMAL":1,"TEXCOORD_0":2},"indices":3,"material":0}]}],
            "nodes":[{"children":[1],"translation":[2,3,4]},{"mesh":0,"scale":[2,3,1]}],"scenes":[{"nodes":[0]}],"scene":0}
        self.doc["accessors"][0].update(min=[0,0,0],max=[1,1,0])
    def audit(self,strict=True):
        self.root.joinpath("asset.gltf").write_text(json.dumps(self.doc))
        return Audit(self.root,"asset.gltf","object",strict).run()
    def codes(self,r): return {e["code"] for e in r["errors"]}
    def test_valid_geometry_and_world_dimensions(self):
        r=self.audit()
        self.assertFalse(r["errors"],r)
        self.assertEqual(r["metrics"]["triangles"],1)
        self.assertEqual(r["metrics"]["rest_geometry_aabb_m"]["min"],[2,3,4])
        self.assertEqual(r["metrics"]["rest_geometry_aabb_m"]["dimensions"],[2,3,0])
        self.assertFalse(r["visual_approval"])
    def test_invalid_index(self):
        p=self.root/"mesh.bin";b=bytearray(p.read_bytes());struct.pack_into("<H",b,100,9);p.write_bytes(b)
        self.assertIn("GEOMETRY_INVALID",self.codes(self.audit()))
    def test_degenerate_triangle(self):
        p=self.root/"mesh.bin";b=bytearray(p.read_bytes());struct.pack_into("<H",b,100,1);p.write_bytes(b)
        self.assertIn("DEGENERATE_TRIANGLES",self.codes(self.audit()))
    def test_inverted_normals(self):
        p=self.root/"mesh.bin";b=bytearray(p.read_bytes());struct.pack_into("<9f",b,36,0,0,-1,0,0,-1,0,0,-1);p.write_bytes(b)
        self.assertIn("NORMAL_OPPOSES_WINDING",self.codes(self.audit()))
    def test_invalid_uv_count(self):
        self.doc["accessors"][2]["count"]=2
        self.assertIn("GEOMETRY_INVALID",self.codes(self.audit()))
    def test_hierarchy_cycle(self):
        self.doc["nodes"][1]["children"]=[0]
        self.assertIn("INVALID_DOCUMENT",self.codes(self.audit()))
    def test_multiple_parents(self):
        self.doc["nodes"].append({"children":[1]})
        self.assertIn("INVALID_DOCUMENT",self.codes(self.audit()))
    def test_zero_scale(self):
        self.doc["nodes"][1]["scale"]=[0,1,1]
        self.assertIn("SINGULAR_TRANSFORM",self.codes(self.audit()))
    def test_missing_texture(self):
        self.doc["images"]=[{"uri":"missing.png"}];self.doc["textures"]=[{"source":0}]
        self.doc["materials"][0]["normalTexture"]={"index":0}
        self.assertIn("INVALID_DOCUMENT",self.codes(self.audit()))
    def test_pbr_factor(self):
        self.doc["materials"][0]["pbrMetallicRoughness"]["metallicFactor"]=2
        self.assertIn("PBR_FACTOR",self.codes(self.audit()))
    def test_trace_drift(self):
        self.root.joinpath("source.py").write_text("changed")
        self.assertIn("INVALID_DOCUMENT",self.codes(self.audit()))
    def test_legacy_warning_not_approval(self):
        del self.doc["asset"]["extras"]
        del self.doc["meshes"][0]["primitives"][0]["attributes"]["NORMAL"]
        r=self.audit(False)
        self.assertFalse(r["errors"]);self.assertIn("NORMAL_MISSING",{x["code"] for x in r["warnings"]})
        self.assertFalse(r["visual_approval"])
    def test_truncated_glb(self):
        self.root.joinpath("bad.glb").write_bytes(b"glTF")
        self.assertIn("INVALID_DOCUMENT",self.codes(Audit(self.root,"bad.glb").run()))
    def test_explicit_contract(self):
        self.doc["nodes"][0]["name"]="anchor";self.doc["nodes"][1]["name"]="panel"
        self.audit()
        contract={"unit":"m","up":"+Y","dimensions_m":[2,3,0],"pivots_local_m":{"anchor":[2,3,4]},
                  "forward":{"node":"panel","local_axis":[0,0,-1],"world_axis":[0,0,-1]}}
        def run():return Audit(self.root,"asset.gltf","object",True,contract=contract).run()
        self.assertFalse(run()["errors"])
        contract["dimensions_m"]=[3,3,0];contract["pivots_local_m"]["anchor"]=[0,0,0];contract["forward"]["world_axis"]=[1,0,0]
        self.assertTrue({"DIMENSION_MISMATCH","PIVOT_MISMATCH","ORIENTATION_MISMATCH"}<=self.codes(run()))
    def test_deterministic(self):self.assertEqual(self.audit(),self.audit())
    def test_engine_reconciliation(self):
        x=self.audit();x["metrics"]["triangles"]=1
        a={"revision":"r","files":[x],"missing_catalog_references":[]}
        y={"path":x["path"],"sha256":x["sha256"],"import_code":0,"mesh_nodes":1,"triangles":1,"unknown_topology":0}
        b={"revision":"r","files":[y]}
        self.assertEqual(reconcile(a,b)["hard_failures"],0)
        y["triangles"]=2
        self.assertEqual(reconcile(a,b)["hard_failures"],1)
        b["revision"]="wrong"
        with self.assertRaises(ValueError):reconcile(a,b)
    def test_transform_rotation(self):
        q=2**-.5;p=point(matrix({"rotation":[0,0,q,q]}),(1,0,0))
        self.assertAlmostEqual(p[0],0);self.assertAlmostEqual(p[1],1)
if __name__=="__main__":unittest.main()
