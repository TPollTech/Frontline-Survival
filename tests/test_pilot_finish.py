import unittest
from tools.asset_pipeline.parametric.pilot_finish import bevel_block,finished_library
from tools.asset_pipeline.parametric.pilot_suite import PILOTS
from tools.asset_pipeline.parametric.lod import BUDGETS

class PilotFinishTests(unittest.TestCase):
    def test_beveled_geometry_is_closed_and_keeps_extent(self):
        a=bevel_block("test",(1,.8,.5),0);b=bevel_block("test",(1,.8,.5),2)
        self.assertTrue(a.closed_oriented());self.assertGreater(a.signed_volume(),0)
        self.assertGreater(len(a.triangles),len(b.triangles))
        lo,hi=a.bounds()
        for n,expected in zip((*lo,*hi),(-.5,0,-.25,.5,.8,.25)):self.assertAlmostEqual(n,expected)
    def test_material_variants_deterministic(self):
        a,b=finished_library(32),finished_library(32)
        self.assertEqual(a.sha256(),b.sha256())
        self.assertNotEqual(a.material("safety_amber").base_color_texture,a.material("painted_steel").base_color_texture)
        self.assertEqual(a.material("safety_amber").normal_texture,a.material("painted_steel").normal_texture)
    def test_geometry_category_coverage(self):
        self.assertEqual({v[0] for v in PILOTS.values()},set(BUDGETS))
if __name__=="__main__":unittest.main()
