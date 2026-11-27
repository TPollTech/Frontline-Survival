"""Test isolated geometry candidates, not engine poses or skinning."""
import unittest
import math
from tools.asset_pipeline.parametric.fps_hand_geometry import palm, dorsal_panel, finger_segment, sleeve


class HandGeometryTests(unittest.TestCase):
    def test_closed_positive_meshes(self):
        meshes = [palm(True), palm(False), dorsal_panel()]
        meshes += [finger_segment(d, distal, .034) for d in range(5) for distal in (False, True)]
        meshes += [sleeve('fps_upper', .42, .068, .075), sleeve('fps_forearm', .39, .052, .063),
                   sleeve('fps_cuff', .105, .054, .062)]
        for mesh in meshes:
            with self.subTest(mesh=mesh.id):
                self.assertTrue(mesh.closed_oriented())
                self.assertGreater(mesh.signed_volume(), 0)
                self.assertTrue(all(math.isfinite(x) for v in mesh.vertices for x in v))

    def test_palm_mirror(self):
        a,b = palm(True), palm(False)
        rounded = lambda vertices: sorted(tuple(round(x,9) for x in p) for p in vertices)
        self.assertEqual(rounded((-x,y,z) for x,y,z in a.vertices), rounded(b.vertices))
        self.assertAlmostEqual(a.signed_volume(), b.signed_volume())
        self.assertEqual(a.triangles,b.triangles)

    def test_distinct_digits_and_taper(self):
        widths = []
        for d in range(5):
            a,b = finger_segment(d,False,.034),finger_segment(d,True,.034)
            lo,hi = a.bounds()
            low,high = b.bounds()
            widths.append(hi[0]-lo[0])
            self.assertGreater(hi[0]-lo[0],high[0]-low[0])
            self.assertLess(lo[1],-.017)
            self.assertGreater(hi[1],.017)
        self.assertEqual(len(set(widths)),5)

    def test_palm_panel_envelope(self):
        for mesh,limit in ((palm(),(.112,.150001,.068)),(dorsal_panel(),(.095,.095,.027))):
            lo,hi=mesh.bounds()
            self.assertTrue(all(b-a <= bound for a,b,bound in zip(lo,hi,limit)))

    def test_determinism_and_budget(self):
        recipes=[lambda:palm(),dorsal_panel]
        recipes += [lambda d=d,k=k:finger_segment(d,k,.034) for d in range(5) for k in (False,True)]
        recipes += [lambda:sleeve('fps_upper',.42,.068,.075),lambda:sleeve('fps_forearm',.39,.052,.063),lambda:sleeve('fps_cuff',.105,.054,.062)]
        meshes=[r() for r in recipes]
        self.assertEqual(meshes,[r() for r in recipes])
        self.assertLessEqual(sum(len(m.triangles) for m in meshes), 4000)

    def test_invalid_inputs(self):
        for f in (lambda:palm(1),lambda:finger_segment(5,False,.03),
                  lambda:finger_segment(0,False,0),lambda:sleeve('invalid',.1,0,.04)):
            with self.assertRaises(ValueError):
                f()

if __name__ == '__main__':
    unittest.main()
