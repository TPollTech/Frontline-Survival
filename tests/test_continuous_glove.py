import unittest
from tools.asset_pipeline.parametric.continuous_glove import build_glove,glove_library,LOW,HIGH
from tools.asset_pipeline.parametric.pilot_finish import finished_library
class ContinuousGloveTests(unittest.TestCase):
    def test_topology_uv_weights_and_lods(self):
        lib=glove_library(finished_library(32),64)
        counts=[]
        for level in range(3):
            scene,render,rig,meta,contract=build_glove(level,lib)
            mesh=scene.meshes[0]
            self.assertEqual(len(scene.meshes),1)
            self.assertTrue(mesh.closed_oriented())
            self.assertEqual(meta["components"],1)
            self.assertEqual(meta["euler_characteristic"],2)
            self.assertEqual(meta["bone_count"],16)
            self.assertGreater(meta["mixed_vertices"],0)
            self.assertEqual(len(meta["deformation_checks"]),4)
            self.assertEqual(len(rig.skins[0].weights),len(mesh.vertices))
            for a,b in zip(mesh.bounds(),(LOW,HIGH)):
                for x,y in zip(a,b):self.assertAlmostEqual(x,y)
            counts.append(len(mesh.triangles))
        self.assertTrue(counts[0]>counts[1]>counts[2])
        self.assertLessEqual(counts[2],3000)
    def test_reproducible_atlas(self):
        lib=finished_library(32)
        self.assertEqual(glove_library(lib,64).sha256(),glove_library(lib,64).sha256())
if __name__=="__main__":unittest.main()
