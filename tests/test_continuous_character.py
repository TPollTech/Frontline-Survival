import unittest
from tools.asset_pipeline.parametric.continuous_character import build_character,character_library,LOW,HIGH
from tools.asset_pipeline.parametric.pilot_finish import finished_library
from tools.asset_pipeline.parametric.intersection_audit import audit,intersects
from tools.asset_pipeline.parametric.lod import BUDGETS
class ContinuousCharacterTests(unittest.TestCase):
    def test_contacts(self):
        a=((0,0,0),(1,0,0),(0,1,0))
        b=((.25,.25,-1),(.25,.25,1),(.75,.25,0))
        self.assertTrue(intersects(a,b))
        self.assertTrue(intersects(a,((.1,.1,0),(.2,.1,0),(.1,.2,0))))
        self.assertFalse(intersects(a,((.8,.8,0),(1,.8,0),(.8,1,0))))
        self.assertFalse(intersects(a,((0,0,1),(1,0,1),(0,1,1))))
        self.assertEqual(audit(a+b,((0,1,2),(3,4,5)))["contact_pairs"],1)
    def test_character_all_lods(self):
        lib=character_library(finished_library(32),64)
        counts=[]
        for level in range(3):
            scene,render,rig,meta,contract=build_character(level,lib)
            mesh=scene.meshes[0]
            self.assertTrue(mesh.closed_oriented())
            self.assertEqual(meta["components"],1)
            self.assertEqual(meta["euler_characteristic"],2)
            self.assertEqual(meta["bone_count"],15)
            self.assertGreater(meta["mixed_vertices"],0)
            self.assertEqual(len(meta["deformation_checks"]),4)
            self.assertEqual(len(meta["combined_pose_checks"]),3)
            for pose in meta["combined_pose_checks"]:
                self.assertGreaterEqual(len(pose["degrees"]),2)
                self.assertEqual([s["fraction"] for s in pose["samples"]],[.25,.5,.75,1.])
                for sample in pose["samples"]:
                    self.assertGreater(sample["moved_vertices"],0)
                    self.assertEqual(sample["contacts"]["contact_pairs"],0)
                    self.assertGreaterEqual(sample["min_area_ratio"],.025)
                    self.assertLessEqual(sample["max_area_ratio"],8)
            self.assertEqual(meta["rest_contacts"]["contact_pairs"],0)
            self.assertTrue(all(c["contacts"]["contact_pairs"]==0 for c in meta["deformation_checks"]))
            self.assertEqual(len(rig.skins[0].weights),len(mesh.vertices))
            # Sidewall uses a separate UV strip; front details must be on -Z.
            half=len(mesh.vertices)//2
            front_uv=[uv for i,uv in zip(render.source_vertices,render.uv) if i>=half and uv[1]<.87]
            back_uv=[uv for i,uv in zip(render.source_vertices,render.uv) if i<half and uv[1]<.87]
            self.assertTrue(front_uv and back_uv)
            self.assertTrue(all(.52-1e-9<=u<=.96+1e-9 for u,v in front_uv))
            self.assertTrue(all(.04-1e-9<=u<=.48+1e-9 for u,v in back_uv))
            self.assertLessEqual(len(mesh.triangles),BUDGETS["character"].triangles[level])
            for a,b in zip(mesh.bounds(),(LOW,HIGH)):
                for x,y in zip(a,b):self.assertAlmostEqual(x,y)
            counts.append(len(mesh.triangles))
            print("CHARACTER_CONTACT_AUDIT",level,meta["rest_contacts"],meta["deformation_checks"])
        self.assertTrue(counts[0]>counts[1]>counts[2])
if __name__=="__main__":unittest.main()
