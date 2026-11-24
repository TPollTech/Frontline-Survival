import json
import tempfile
import unittest
from pathlib import Path
from tools.asset_pipeline.live_catalog import build, canonical, sha

class CatalogTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name)
        self.put("assets/catalog/manifest.json",json.dumps({"assets":[],"resources":{},"source_registry":{},"known_dynamic_gaps":[]}))
    def put(self,p,data):
        f=self.root/p
        f.parent.mkdir(parents=True,exist_ok=True)
        f.write_text(data,encoding="utf-8")
    def catalog(self,paths,runtime=None):
        return build(self.root,paths=paths,revision="fixture",runtime=runtime)
    def test_discovery_and_reference(self):
        self.put("assets/new.glb","model bytes")
        self.put("scenes/map.tscn",'[ext_resource path="res://assets/new.glb"]')
        c=self.catalog(["assets/new.glb","scenes/map.tscn"])
        self.assertEqual(c["counts"]["assets"],2)
        self.assertEqual(c["resources"]["assets/new.glb"]["references"],[{"source":"scenes/map.tscn","line":1}])
        a=next(a for a in c["assets"] if a["id"]=="file:assets/new.glb")
        self.assertEqual(a["preview"]["resource"],"assets/new.glb")
        self.assertFalse(a["validation"]["approved"])
    def test_new_unknown_and_sidecar(self):
        self.put("assets/new.foo","unknown")
        self.put("assets/new.foo.import","metadata")
        c=self.catalog(["assets/new.foo","assets/new.foo.import"])
        self.assertEqual(len(c["resources"]),2)
        self.assertEqual(len(c["assets"]),1)
        self.assertEqual(c["assets"][0]["category"],"unclassified")
    def test_literal_and_dynamic_gaps(self):
        self.put("scripts/game.gd",'load("res://assets/missing.glb")\nload("res://assets/%s.glb" % id)\nvar m=ArrayMesh.new()')
        c=self.catalog(["scripts/game.gd"])
        self.assertEqual(len(c["missing_literal_references"]),1)
        self.assertEqual(len(c["dynamic_references"]),1)
        self.assertEqual(c["runtime_candidates"],["scripts/game.gd"])
    def test_relative_gltf_dependencies(self):
        self.put("assets/new.gltf",json.dumps({"buffers":[{"uri":"data.bin"}]}))
        self.put("assets/data.bin","buffer")
        c=self.catalog(["assets/new.gltf"])
        self.assertIn("assets/data.bin",c["resources"])
    def test_deterministic_and_changed(self):
        self.put("assets/a.glb","a")
        self.put("assets/b.png","b")
        a=self.catalog(["assets/a.glb","assets/b.png"])
        self.assertEqual(canonical(a),canonical(self.catalog(["assets/b.png","assets/a.glb"])))
        self.put("assets/a.glb","changed")
        self.assertNotEqual(canonical(a),canonical(self.catalog(["assets/a.glb","assets/b.png"])))
    def test_missing_baseline(self):
        self.put("assets/catalog/manifest.json",json.dumps({"assets":[],"resources":{"assets/gone.glb":{"category":"model","git_blob_sha1":"0"*40}},"source_registry":{},"known_dynamic_gaps":[]}))
        c=self.catalog([])
        self.assertEqual(c["resources"]["assets/gone.glb"]["status"],"missing")
        self.assertEqual(c["assets"][0]["preview"]["mode"],"unavailable")
    def test_stale_runtime(self):
        with self.assertRaisesRegex(ValueError,"stale runtime"):
            self.catalog([],{"kind":"frontline_runtime_inventory","schema_version":1,"commit":"old","failures":[]})
    def test_unsafe_path(self):
        with self.assertRaises(ValueError):
            self.catalog(["assets/../bad.glb"])

if __name__=="__main__":unittest.main()
