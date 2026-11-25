import json
import base64
from tools.asset_pipeline.runtime_catalog_evidence import dynamic_evidence,geometry_evidence
import struct
import subprocess
import tempfile
import unittest
from pathlib import Path
from tools.asset_pipeline.live_catalog import build, canonical, sha, resolve_gltf_uri, runtime_resource_paths, sample_metrics

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

    def test_shared_character_recipes_are_linked_not_preview_assets(self):
        helper="scripts/character_geometry.gd"
        families={
            "viewmodel:hands":("scripts/player.gd",["sleeve"]),
            "enemy:legacy":("scripts/enemy.gd",["joint","padded","capsule"]),
            "ally:legacy":("scripts/ally.gd",["joint","padded","capsule"]),
            "character:quaternius_equipment":("scripts/quaternius_soldier_visual.gd",["capsule","box"]),
        }
        assets=[]
        for aid,(p,names) in families.items():
            self.put(p,'const CharacterGeometry = preload("res://'+helper+'")\n'+"\n".join("CharacterGeometry."+n+"()" for n in names))
            assets.append({"id":aid,"category":"character","source":{"path":p,"kind":"godot_recipe"},"outputs":[],"dependencies":{"sources":[],"assets":[],"resources":[]},"preview":{"resource":None},"validation":{}})
        self.put(helper,"\n".join("static func "+n+"():\n    MeshInstance3D.new()" for n in ("joint","padded","capsule","box","sleeve")))
        self.put("scripts/model_surface.gd","extends RefCounted")
        self.put("assets/catalog/manifest.json",json.dumps({"assets":assets,"resources":{},"source_registry":{},"known_dynamic_gaps":[]}))
        paths=[helper,"scripts/model_surface.gd"]+[p for p,_ in families.values()]
        c=self.catalog(paths)
        self.assertEqual(len(c["assets"]),4)
        self.assertNotIn(helper,c["runtime_candidates"])
        for a in c["assets"]:
            self.assertIn(helper,a["dependencies"]["sources"])
            self.assertEqual(a["canonical_shared_recipes"]["functions"],families[a["id"]][1])
            self.assertEqual(a["canonical_shared_recipes"]["fingerprint"],c["sources"][helper])
            self.assertFalse(a["canonical_shared_recipes"]["approved"])
        self.assertEqual(canonical(c),canonical(self.catalog(paths)))
        self.put("scripts/ally.gd",'const CharacterGeometry = preload("res://'+helper+'")')
        with self.assertRaisesRegex(ValueError,"missing shared character recipe"):
            self.catalog(paths)


    def test_world_asset_recipes_are_linked_to_real_families(self):
        helper="scripts/world_asset_geometry.gd"
        families={
            "map:campo_de_testes":("scripts/main.gd",["world_box","cylinder"]),
            "environment:lighting":("scripts/main.gd",["depot_environment","depot_sun"]),
            "object:loot":("scripts/loot_pickup.gd",["machined"]),
            "object:turret":("scripts/turret.gd",["cylinder","machined"]),
            "object:grenade":("scripts/frag_grenade.gd",["cylinder","box"]),
        }
        assets=[]
        consumers={}
        for aid,(p,names) in families.items():
            consumers.setdefault(p,set()).update(names)
            assets.append({"id":aid,"category":aid.split(":")[0],"source":{"path":p,"kind":"godot_recipe"},"outputs":[],"dependencies":{"sources":[],"assets":[],"resources":[]},"preview":{"resource":None},"validation":{}})
        for p,names in consumers.items():
            self.put(p,'const WorldAssetGeometry = preload("res://'+helper+'")\n'+"\n".join("WorldAssetGeometry."+n+"()" for n in sorted(names)))
        self.put(helper,"\n".join("static func "+n+"():\n    BoxMesh.new()" for n in ("box","machined","world_box","cylinder","depot_environment","depot_sun")))
        self.put("scripts/model_surface.gd","extends RefCounted")
        self.put("assets/catalog/manifest.json",json.dumps({"assets":assets,"resources":{},"source_registry":{},"known_dynamic_gaps":[]}))
        paths=[helper,"scripts/model_surface.gd"]+list(consumers)
        c=self.catalog(paths)
        self.assertEqual(len(c["assets"]),5)
        self.assertNotIn(helper,c["runtime_candidates"])
        for a in c["assets"]:
            self.assertIn(helper,a["dependencies"]["sources"])
            self.assertEqual(a["canonical_shared_recipes"]["functions"],families[a["id"]][1])
            self.assertEqual(a["canonical_shared_recipes"]["fingerprint"],c["sources"][helper])
            self.assertFalse(a["canonical_shared_recipes"]["approved"])
        self.assertEqual(canonical(c),canonical(self.catalog(paths)))
        self.put("scripts/turret.gd",'const WorldAssetGeometry = preload("res://'+helper+'")')
        with self.assertRaisesRegex(ValueError,"missing shared world recipe"):
            self.catalog(paths)

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
    def test_gltf_dependency_paths_and_hashes(self):
        self.put("assets/models/new.gltf",json.dumps({"buffers":[{"uri":"../buffers/data.bin"}],"images":[{"uri":"../textures/metal%20a.png"},{"uri":"https://example.invalid/x.png"},{"uri":"../../../outside.png"},{"uri":"data:image/png;base64,AA=="}]}))
        self.put("assets/buffers/data.bin","buffer")
        self.put("assets/textures/metal a.png","image")
        c=self.catalog(["assets/models/new.gltf"])
        deps=c["resources"]["assets/models/new.gltf"]["gltf_dependencies"]
        self.assertEqual(deps,[{"uri":"../buffers/data.bin","path":"assets/buffers/data.bin"},{"uri":"../textures/metal%20a.png","path":"assets/textures/metal a.png"}])
        self.assertEqual(c["resources"]["assets/buffers/data.bin"]["sha256"],sha(b"buffer"))
        self.assertEqual(len(c["missing_literal_references"]),2)
        self.assertEqual(canonical(c),canonical(self.catalog(["assets/models/new.gltf"])))

    def test_glb_external_dependency(self):
        p=self.root/"assets/new.glb"
        p.parent.mkdir(parents=True,exist_ok=True)
        doc=json.dumps({"asset":{"version":"2.0"},"buffers":[{"uri":"external.bin","byteLength":4}]}).encode()
        doc+=b" "*((-len(doc))%4)
        p.write_bytes(struct.pack("<4sII",b"glTF",2,20+len(doc))+struct.pack("<I4s",len(doc),b"JSON")+doc)
        self.put("assets/external.bin","data")
        c=self.catalog(["assets/new.glb"])
        self.assertEqual(c["resources"]["assets/new.glb"]["gltf_dependencies"],[{"uri":"external.bin","path":"assets/external.bin"}])

    def test_runtime_discovers_resource_and_rejects_drift(self):
        self.put("custom/model.glb","model bytes")
        def git(*args):
            return subprocess.check_output(["git","-C",str(self.root),*args]).decode().strip()
        git("init","-q")
        git("add",".")
        git("-c","user.name=Fixture","-c","user.email=fixture@example.invalid","commit","-qm","fixture")
        revision=git("rev-parse","HEAD")
        runtime={"kind":"frontline_runtime_inventory","schema_version":1,"commit":revision,"failures":[],
                 "samples":[{"id":"sample","families":[],"nodes":[{"mesh":{"path":"res://custom/model.glb"}},{"mesh":{"path":"res://custom/missing.glb"}}]}],
                 "query_records":[],"limitations":[]}
        catalog=build(self.root,paths=[],revision=revision,runtime=runtime)
        self.assertEqual(catalog["resources"]["custom/model.glb"]["observations"],["sample"])
        self.assertEqual(catalog["runtime_samples"]["sample"]["mesh_nodes"],2)
        self.assertEqual(catalog["runtime_resource_gaps"],[{"sample":"sample","path":"custom/missing.glb","reason":"not a local file"}])
        self.assertEqual(next(a for a in catalog["assets"] if a["id"]=="file:custom/model.glb")["validation"]["runtime"],"sampled")
        self.put("custom/model.glb","changed")
        with self.assertRaisesRegex(ValueError,"runtime source drift"):
            build(self.root,paths=[],revision=revision,runtime=runtime)

    def test_unsafe_gltf_uris(self):
        for uri in ("../../../x","https://example.invalid/x","//example.invalid/x","/assets/x","%2Fx","foo%2fbar","foo%5cbar","x?y=1","x#y","%00x","file:x"):
            with self.subTest(uri=uri),self.assertRaises(ValueError):
                resolve_gltf_uri("assets/models/a.gltf",uri)

    def test_runtime_paths_normalize_subresources(self):
        sample={"nodes":[{"mesh":{"path":"res://assets/model.glb::Mesh_1","surfaces":[{"effective_material":{"albedo_texture":{"path":"res://assets/tex.png::Image"},"roughness_texture":None}}]},"audio":{"path":"res://assets/audio.wav"}},{"mesh":{"path":None}}]}
        self.assertEqual(set(runtime_resource_paths(sample)),{"assets/model.glb","assets/tex.png","assets/audio.wav"})


    def test_runtime_sample_metrics_scope_and_unknown_topology(self):
        sample={"id":"s","families":["z","a"],"nodes":[
            {"mesh":{"lod_bias":1.0,"surfaces":[{"vertices":3,"triangles":1},{"vertices":2,"triangles":None}]}},
            {"collision":{"class":"BoxShape3D","disabled":False}},
            {"collision":{"class":"SphereShape3D","disabled":True}}]}
        m=sample_metrics(sample)
        self.assertEqual(m["scope"],"whole_sample_subtree")
        self.assertEqual((m["vertices"],m["triangles"],m["unknown_triangle_surfaces"]),(5,1,1))
        self.assertEqual(m["collision_classes"],{"BoxShape3D":1})
        self.assertEqual((m["enabled_colliders"],m["disabled_colliders"]),(1,1))
        self.assertEqual(m["lod_bias_counts"],{"1.0":1})
        self.assertFalse(m["lod_indices_measured"])
        self.assertFalse(m["approved"])
        self.assertEqual(m["families"],["a","z"])

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
    def test_dynamic_probe_reconciliation(self):
        ref={"source":"scripts/player.gd","line":1,"target":"assets/%s_%s.glb"}
        row={"source":ref["source"],"pattern":ref["target"],"arguments":["a","body"],"path":"assets/a_body.glb","exists":True,"guarded":True}
        resources={row["path"]:{"status":"new","sha256":"a"*64}}
        result=dynamic_evidence([ref],{"dynamic_probes":[row]},resources,{"fps_a___hip":{row["path"]}})[0]
        self.assertEqual(result["status"],"finite_domain_probed")
        self.assertEqual(result["candidates"][0]["observed_samples"],["fps_a___hip"])
        with self.assertRaisesRegex(ValueError,"expansion mismatch"):
            dynamic_evidence([ref],{"dynamic_probes":[{**row,"path":"bad"}]},resources,{})
    def test_geometry_buffer_integrity_and_mapping(self):
        data=b"godot fixture bytes";digest=sha(data)
        row={"encoding":"godot_variant_v4_base64","bytes":len(data),"data":base64.b64encode(data).decode(),"primitive":3}
        sample={"id":"map","nodes":[{"path":".","mesh":{"path":"","surfaces":[{"buffer_sha256":digest,"primitive":3}]}}]}
        runtime={"geometry_buffers":{digest:row},"samples":[sample]}
        index,compositions=geometry_evidence(runtime)
        self.assertEqual(index[digest]["sample_ids"],["map"])
        self.assertEqual(compositions["map"]["nodes"][0]["buffer_sha256"],[digest])
        with self.assertRaisesRegex(ValueError,"integrity"):
            geometry_evidence({**runtime,"geometry_buffers":{digest:{**row,"bytes":1}}})
        with self.assertRaisesRegex(ValueError,"missing procedural"):
            geometry_evidence({**runtime,"geometry_buffers":{}})
    def test_unsafe_path(self):
        with self.assertRaises(ValueError):
            self.catalog(["assets/../bad.glb"])

if __name__=="__main__":unittest.main()
