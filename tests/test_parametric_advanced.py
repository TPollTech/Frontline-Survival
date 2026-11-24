"""Analytical tests on neutral technical solids; no production assets."""
import math
import os
import unittest
from tools.asset_pipeline.parametric import (Box, Extrusion, Revolution, PythonBackend,
    BlenderBackend, BlenderError, MeshSpec, Transform)
from tools.asset_pipeline.parametric.advanced import triangulate_profile, signed_area

L_PROFILE=((0,0),(3,0),(3,1),(1,1),(1,2),(0,2))

class AdvancedTests(unittest.TestCase):
    def setUp(self):
        self.backend=PythonBackend()

    def test_concave_extrusion(self):
        m=self.backend.build(Extrusion("bracket",L_PROFILE,0.5,-0.25))
        self.assertEqual(m.bounds(),((0,-0.25,0),(3,0.25,2)))
        self.assertEqual(len(m.vertices),12)
        self.assertEqual(len(m.triangles),20)
        self.assertTrue(m.closed_oriented())
        self.assertAlmostEqual(m.signed_volume(),2.)

    def test_cap_area(self):
        p,faces=triangulate_profile(L_PROFILE)
        self.assertEqual(len(faces),len(p)-2)
        self.assertAlmostEqual(signed_area(p),4.)

    def test_profile_order_deterministic(self):
        a=self.backend.build(Extrusion("bracket",L_PROFILE,1))
        for p in (L_PROFILE[2:]+L_PROFILE[:2],L_PROFILE[::-1]):
            self.assertEqual(a,self.backend.build(Extrusion("bracket",p,1)))

    def test_bad_profiles(self):
        for p in (((0,0),(1,1),(0,1),(1,0)),((0,0),(1,0),(1,0),(0,1)),
                  ((0,0),(1,0),(2,0),(0,1)),((0,0),(1,0),(0,0.0)),((0,0),(math.nan,1),(1,0))):
            with self.subTest(profile=p),self.assertRaises(ValueError):
                Extrusion("bad",p,1)

    def test_height(self):
        for h in (0,-1,math.inf):
            with self.subTest(height=h),self.assertRaises(ValueError):
                Extrusion("bad",L_PROFILE,h)

    def test_revolution_cylinder(self):
        m=self.backend.build(Revolution("solid",((0,-1),(1,-1),(1,1),(0,1)),32))
        self.assertTrue(m.closed_oriented())
        self.assertEqual(len(m.vertices),66)
        self.assertEqual(len(m.triangles),128)
        self.assertAlmostEqual(m.signed_volume(),32*math.sin(math.tau/32))
        self.assertAlmostEqual(m.bounds()[0][1],-1)

    def test_revolution_hollow(self):
        n=64
        m=self.backend.build(Revolution("ring",((0.5,-1),(1,-1),(1,1),(0.5,1)),n))
        self.assertTrue(m.closed_oriented())
        self.assertEqual(len(m.vertices),4*n)
        self.assertEqual(len(m.triangles),8*n)
        self.assertAlmostEqual(m.signed_volume(),n*math.sin(math.tau/n)*0.75)

    def test_revolution_cone(self):
        n=48
        m=self.backend.build(Revolution("cone",((0,0),(1,0),(0,2)),n))
        self.assertTrue(m.closed_oriented())
        self.assertEqual(len(m.vertices),n+2)
        self.assertAlmostEqual(m.signed_volume(),n*math.sin(math.tau/n)/3)

    def test_revolution_steps(self):
        p=((0,0),(1,0),(1,1),(0.5,1),(0.5,2),(0,2))
        n=64
        m=self.backend.build(Revolution("step",p,n))
        self.assertTrue(m.closed_oriented())
        self.assertAlmostEqual(m.signed_volume(),n*0.5*math.sin(math.tau/n)*1.25)
        self.assertEqual(m,self.backend.build(Revolution("step",p[::-1],n)))

    def test_invalid_revolution(self):
        for p in (((-1,0),(1,0),(1,1)),((0,0),(1,0),(0,1),(1,2),(0,3))):
            with self.subTest(profile=p),self.assertRaises(ValueError):
                Revolution("bad",p,32)
        for seg in (0,513,True):
            with self.subTest(segments=seg),self.assertRaises(ValueError):
                Revolution("bad",((0,0),(1,0),(1,1),(0,1)),seg)

    def test_boolean_validation(self):
        b=self.backend.build(Box("block",(1,1,1)))
        with self.assertRaises(ValueError):
            BlenderBackend().boolean("bad",b,b,"xor")
        m=MeshSpec("open",((0,0,0),(1,0,0),(0,1,0)),((0,1,2),))
        with self.assertRaises(ValueError):
            BlenderBackend().boolean("bad",b,m,"difference")

    def test_bevel_validation(self):
        b=self.backend.build(Box("block",(1,1,1)))
        for width in (0,-1,math.inf):
            with self.subTest(width=width),self.assertRaises(ValueError):
                BlenderBackend().bevel(b,width)

class AdvancedBlenderTests(unittest.TestCase):
    def setUp(self):
        self.backend=BlenderBackend()
        if not self.backend.available:
            if os.environ.get("FRONTLINE_REQUIRE_BLENDER")=="1":
                self.fail("actual Blender required")
            self.skipTest("optional Blender absent")
        self.block=PythonBackend().build(Box("block",(2,2,2)))

    def test_boolean_volumes(self):
        t=Transform.translation((0.5,0.75,0.25))
        overlap=1.5*1.25*1.75
        for op,expected in (("union",16-overlap),("difference",8-overlap),("intersection",overlap)):
            with self.subTest(op=op):
                m=self.backend.boolean("result",self.block,self.block,op,right_transform=t)
                self.assertTrue(m.closed_oriented())
                self.assertAlmostEqual(m.signed_volume(),expected,places=5)
        self.assertAlmostEqual(self.block.signed_volume(),8.)

    def test_intersection_bounds_and_topology(self):
        m=self.backend.boolean("overlap",self.block,self.block,"intersection",
                               right_transform=Transform.translation((0.5,0.75,0.25)))
        self.assertEqual(m.bounds(),((-0.5,-0.25,-0.75),(1,1,1)))
        self.assertTrue(m.closed_oriented())
        self.assertAlmostEqual(m.signed_volume(),1.5*1.25*1.75,places=5)
        # The overlapping region is a rectangular solid, with no internal seams.
        self.assertEqual(len(m.vertices),8)
        self.assertEqual(len(m.triangles),12)

    def test_empty_intersection(self):
        # Reject a genuine empty evaluated mesh, not an arbitrary process/API failure.
        with self.assertRaisesRegex(BlenderError,"empty boolean result"):
            self.backend.boolean("empty",self.block,self.block,"intersection",right_transform=Transform.translation((5,0,0)))

    def test_disjoint_boolean_solids(self):
        t=Transform.translation((5,0,0))
        for op,expected in (("union",16.),("difference",8.)):
            with self.subTest(op=op):
                m=self.backend.boolean("disjoint",self.block,self.block,op,right_transform=t)
                self.assertTrue(m.closed_oriented())
                self.assertAlmostEqual(m.signed_volume(),expected,places=5)
                if op=="union":
                    self.assertEqual(m.bounds(),((-1,-1,-1),(6,1,1)))
                else:
                    self.assertEqual(m.bounds(),self.block.bounds())

    def test_contained_boolean_cavity(self):
        inner=PythonBackend().build(Box("inner",(1,1,1)))
        m=self.backend.boolean("cavity",self.block,inner,"difference")
        self.assertTrue(m.closed_oriented())
        self.assertAlmostEqual(m.signed_volume(),7.,places=5)
        self.assertEqual(m.bounds(),self.block.bounds())

    def test_rounded_bevel(self):
        a=self.backend.bevel(self.block,0.05,1)
        b=self.backend.bevel(self.block,0.05,3)
        self.assertTrue(a.closed_oriented() and b.closed_oriented())
        self.assertGreater(len(b.triangles),len(a.triangles))
        self.assertLess(a.signed_volume(),8.)
        self.assertLess(b.signed_volume(),8.)
        for actual,expected in zip(b.bounds(),self.block.bounds()):
            for x,y in zip(actual,expected):
                self.assertAlmostEqual(x,y,places=6)

    def test_blender_roundtrip_concave(self):
        m=self.backend.build(Extrusion("bracket",L_PROFILE,0.5))
        self.assertTrue(m.closed_oriented())
        self.assertAlmostEqual(m.signed_volume(),2.,places=6)

if __name__=="__main__":
    unittest.main()
