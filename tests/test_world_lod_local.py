"""Synthetic report fixtures: tests of the verifier, never engine evidence."""
import copy
import json
from pathlib import Path
import struct
import tempfile
import unittest
try:
    from tools.asset_pipeline.world_lod_local import FAMILIES, DISTANCES, LEVELS, verify_report, verify_directory
except ModuleNotFoundError:
    from world_lod_local import FAMILIES, DISTANCES, LEVELS, verify_report, verify_directory


def fixture():
    assemblies,checks=[],[]
    for family,(count,category,blocking,exact) in FAMILIES.items():
        for i in range(count):
            index=len(assemblies)
            triangles=list(exact or ((3456,864,384) if i<2 else (2592,648,288)))
            policy="existing_box" if blocking else "nonblocking"
            slots={"container_corners":2,"barrel":4,"shop":2,"light_post":3}.get(family,triangles[0]//432)
            assemblies.append(dict(family=family,path=f"/fixture/{index}",category=category,collision_policy=policy,colliders=int(blocking),collision_triangles=0,hardware_validated=False,limits_provisional=True,triangles_by_level=triangles,material_slots=slots))
            for distance,level in zip(DISTANCES,LEVELS):
                checks.append(dict(assembly=index,family=family,category=category,distance_m=distance,level=level,triangles=triangles[level],collision_policy=policy,shape_id_unchanged=True,collider_size=[1,1,1] if blocking else [0,0,0],hit_z=0.0 if blocking else None))
    return dict(assemblies=assemblies,checks=checks,hardware_validated=False)


class WorldLODLocalTests(unittest.TestCase):
    def test_valid_fixture(self):
        summary=verify_report(fixture())
        self.assertEqual(summary["triangles_by_level"],[49248,10584,4128])
        self.assertEqual(summary["checks"],207)
        self.assertFalse(summary["visual_reviewed"])
        self.assertFalse(summary["hardware_validated"])

    def test_missing_row(self):
        r=fixture(); r["checks"].pop()
        with self.assertRaisesRegex(ValueError,"assembly/check count"): verify_report(r)

    def test_wrong_family(self):
        r=fixture(); r["assemblies"][-1]["family"]="barrel"
        with self.assertRaisesRegex(ValueError,"family coverage"): verify_report(r)

    def test_duplicate_path(self):
        r=fixture(); r["assemblies"][-1]["path"]=r["assemblies"][0]["path"]
        with self.assertRaisesRegex(ValueError,"duplicate assembly"): verify_report(r)

    def test_wrong_post_triangles(self):
        r=fixture(); r["assemblies"][-1]["triangles_by_level"][2]=145
        with self.assertRaisesRegex(ValueError,"triangle recipe"): verify_report(r)

    def test_wrong_level(self):
        r=fixture(); r["checks"][2]["level"]=0
        with self.assertRaisesRegex(ValueError,"LOD sequence"): verify_report(r)

    def test_collider_mutation(self):
        r=fixture(); r["checks"][2]["collider_size"]=[2,1,1]
        with self.assertRaisesRegex(ValueError,"collider invariant"): verify_report(r)

    def test_ray_mutation(self):
        r=fixture(); r["checks"][2]["hit_z"]=0.1
        with self.assertRaisesRegex(ValueError,"ray invariant"): verify_report(r)

    def test_nonblocking_ray(self):
        r=fixture(); r["checks"][-1]["hit_z"]=0.0
        with self.assertRaisesRegex(ValueError,"ray invariant"): verify_report(r)

    def test_no_hardware_claim(self):
        r=fixture(); r["hardware_validated"]=True
        with self.assertRaisesRegex(ValueError,"hardware approval"): verify_report(r)

    def test_capture_headers_and_missing_capture(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            (root/"world-lod-report.json").write_text(json.dumps(fixture()))
            # Header-only synthetic bytes; not valid rendered images.
            header=b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR"+struct.pack(">II",1280,720)+b"fixture-only"
            for family in FAMILIES:
                for suffix in ("lod","fixed-lod"):
                    for level in range(3): (root/f"{family}-{suffix}{level}.png").write_bytes(header)
            self.assertEqual(verify_directory(root)["capture_headers_checked"],30)
            path=root/"light_post-fixed-lod2.png"
            path.write_bytes(b"wrong")
            with self.assertRaisesRegex(ValueError,"invalid PNG header"): verify_directory(root)
            path.unlink()
            with self.assertRaises(FileNotFoundError): verify_directory(root)

if __name__=="__main__": unittest.main()
