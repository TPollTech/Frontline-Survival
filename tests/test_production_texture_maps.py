"""Focused tests of the candidate pixel buffers, not engine integration."""
import hashlib
import math
import unittest
from tools.asset_pipeline.parametric.production_texture_maps import STYLE, height_at, surface_pixels

PROFILES = {"exposed_metal": (1., .42), "painted_metal": (0., .58),
            "polymer": (0., .72), "rubber": (0., .88), "wood": (0., .66),
            "brass": (1., .48)}


def factors(profile):
    m, r = PROFILES[profile]
    return {"metallic": m, "roughness": r}


class PixelTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.maps = {p: surface_pixels(p, factors(p), 64) for p in PROFILES}

    def test_coverage_and_dimensions(self):
        self.assertEqual(set(STYLE), set(PROFILES))
        for maps in self.maps.values():
            self.assertEqual(set(maps), {"base_color", "normal", "orm"})
            self.assertTrue(all(len(b) == 64*64*3 for b in maps.values()))

    def test_determinism(self):
        for p, maps in self.maps.items():
            self.assertEqual(maps, surface_pixels(p, factors(p), 64))

    def test_distinct_normal_maps(self):
        self.assertEqual(len({hashlib.sha256(m["normal"]).hexdigest() for m in self.maps.values()}), 6)

    def test_neutral_base_color(self):
        for m in self.maps.values():
            b = m["base_color"]
            self.assertTrue(all(b[i] == b[i+1] == b[i+2] for i in range(0,len(b),3)))
            self.assertGreater(len(set(b)), 1)

    def test_normal_length_and_positive_z(self):
        for m in self.maps.values():
            b = m["normal"]
            for i in range(0,len(b),3):
                x,y,z = (2*q/255-1 for q in b[i:i+3])
                self.assertGreater(z,0)
                self.assertLess(abs(x*x+y*y+z*z-1),.025)

    def test_orm_absolute_channels(self):
        for p,m in self.maps.items():
            metal, rough = PROFILES[p]
            b = m["orm"]
            self.assertEqual(set(b[::3]),{255})
            self.assertEqual(set(b[2::3]),{round(metal*255)})
            self.assertLess(abs(sum(b[1::3])/len(b[1::3])/255-rough),.03)

    def test_periodic_height_and_gradient(self):
        for p in PROFILES:
            for u,v in ((0.,.23),(.31,0.),(.91,.77)):
                for dx,dy in ((0,0),(.001,0),(0,.001),(-.001,0),(0,-.001)):
                    a=height_at(p,u+dx,v+dy)
                    self.assertAlmostEqual(a,height_at(p,u+dx+1,v+dy),places=10)
                    self.assertAlmostEqual(a,height_at(p,u+dx,v+dy+1),places=10)

    def test_seed_changes_pattern(self):
        self.assertNotEqual(self.maps["wood"],surface_pixels("wood",factors("wood"),64,206))

    def test_bad_inputs(self):
        for p, f, s in (("missing",factors("wood"),64),("wood",factors("wood"),65),
                        ("wood",{"metallic":float("nan"),"roughness":.5},64)):
            with self.assertRaises(ValueError):
                surface_pixels(p,f,s)

if __name__ == "__main__":
    unittest.main()
