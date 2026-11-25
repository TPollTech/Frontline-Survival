import unittest
from tools.asset_pipeline.parametric.pilot_art import ART_NAMES,BACKEND_PARTS,detailed
from tools.asset_pipeline.parametric.pilot_suite import PILOTS
from tools.asset_pipeline.parametric.blender_backend import BlenderBackend

class PilotArtTests(unittest.TestCase):
    def test_art_backend_and_envelopes(self):
        self.assertTrue(BlenderBackend().available,"actual Blender required")
        for name,id in sorted(BACKEND_PARTS):
            p=next(p for p in PILOTS[name][1] if p["id"]==id)
            a=detailed(name,p,0);b=detailed(name,p,2)
            self.assertTrue(a.closed_oriented())
            self.assertGreater(a.signed_volume(),0)
            self.assertGreater(len(a.triangles),len(b.triangles))
            lo,hi=a.bounds();x,y,z=p["size"]
            for v,e in zip((*lo,*hi),(-x/2,0,-z/2,x/2,y,z/2)):self.assertAlmostEqual(v,e,places=5)
    def test_wheel_axis_and_extent(self):
        p=next(p for p in PILOTS["utility_cart"][1] if p["id"]=="wheel_0")
        for level in range(3):
            m=detailed("utility_cart",p,level)
            self.assertTrue(m.closed_oriented());self.assertGreater(m.signed_volume(),0)
            lo,hi=m.bounds()
            for actual,expected in zip((b-a for a,b in zip(lo,hi)),p["size"]):self.assertAlmostEqual(actual,expected,places=5)
if __name__=="__main__":unittest.main()
