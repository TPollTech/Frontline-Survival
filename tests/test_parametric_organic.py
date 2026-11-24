"""Analytical and actual Blender roundtrips for neutral organic fixtures."""
import math
import os
import unittest
from tools.asset_pipeline.parametric import (
    Box, PythonBackend, BlenderBackend, BezierCurve, BezierPatch,
    LoftSection, OrganicLoft, CustomTopology)

def patch():
    return BezierPatch("patch",tuple(tuple((i/3, 0.2 if i in (1,2) and j in (1,2) else 0., j/3)
                      for j in range(4)) for i in range(4)),8,10)

def loft():
    return OrganicLoft("loft",(LoftSection(0,(0,0),(0.5,0.35)),
        LoftSection(0.6,(0.1,0),(0.65,0.45),0.2),
        LoftSection(1.2,(0.15,0.1),(0.3,0.25),0.5)),32,8)

class OrganicTests(unittest.TestCase):
    def setUp(self):
        self.b=PythonBackend()

    def test_curve_endpoints_tangents(self):
        c=BezierCurve((((0,0,0),(1,0,0),(1,1,0),(2,1,0)),))
        self.assertEqual(c.point(0,0),(0,0,0))
        self.assertEqual(c.point(0,1),(2,1,0))
        self.assertEqual(c.point(0,0.5),(1,0.5,0))
        self.assertEqual(c.tangent(0,0),(3,0,0))
        self.assertEqual(c.tangent(0,1),(3,0,0))

    def test_curve_join_and_sampling(self):
        c=BezierCurve((((0,0,0),(1,0,0),(2,0,0),(3,0,0)),
                        ((3,0,0),(4,0,0),(4,1,0),(5,1,0))),True)
        points=c.sample(8)
        self.assertEqual(len(points),17)
        self.assertEqual(points[8],(3,0,0))
        self.assertEqual(c.tangent(0,1),c.tangent(1,0))
        self.assertEqual(points,c.sample(8))

    def test_curve_rejections(self):
        a=((0,0,0),(1,0,0),(2,0,0),(3,0,0))
        with self.assertRaises(ValueError):
            BezierCurve((a,a))
        with self.assertRaises(ValueError):
            BezierCurve((a,((3,0,0),(3,1,0),(4,1,0),(5,1,0))),True)
        with self.assertRaises(ValueError):
            BezierCurve((a,)).point(0,1.1)
        with self.assertRaises(ValueError):
            BezierCurve((a,)).sample(True)

    def test_patch_boundaries_and_center(self):
        p=patch()
        self.assertEqual(p.point(0,0),(0,0,0))
        self.assertEqual(p.point(1,1),(1,0,1))
        self.assertAlmostEqual(p.point(0.5,0.5)[1],0.1125)
        m=self.b.build(p)
        self.assertEqual(len(m.vertices),99)
        self.assertEqual(len(m.triangles),160)
        self.assertFalse(m.closed_oriented())
        self.assertEqual(m,self.b.build(p))

    def test_patch_reject_degenerate(self):
        p=BezierPatch("flat",(((0,0,0),)*4,)*4,2,2)
        with self.assertRaises(ValueError):
            self.b.build(p)

    def test_loft_closed_and_deterministic(self):
        p=loft()
        m=self.b.build(p)
        self.assertEqual(len(m.vertices),17*32+2)
        self.assertEqual(len(m.triangles),17*64)
        self.assertTrue(m.closed_oriented())
        self.assertGreater(m.signed_volume(),0)
        self.assertEqual((m.bounds()[0][1],m.bounds()[1][1]),(0,1.2))
        self.assertEqual(m,self.b.build(p))

    def test_loft_prismatic_volume(self):
        n=32
        p=OrganicLoft("ellipse",(LoftSection(0,(0,0),(2,1)),LoftSection(3,(0,0),(2,1))),n,4)
        m=self.b.build(p)
        self.assertAlmostEqual(m.signed_volume(),n*0.5*2*math.sin(math.tau/n)*3)
        self.assertTrue(m.closed_oriented())

    def test_loft_invalid_parameters(self):
        with self.assertRaises(ValueError):
            LoftSection(0,(0,0),(0,1))
        s=LoftSection(0,(0,0),(1,1))
        with self.assertRaises(ValueError):
            OrganicLoft("bad",(s,s))
        with self.assertRaises(ValueError):
            OrganicLoft("bad",(s,LoftSection(1,(0,0),(1,1))),512,256)

    def test_custom_quad(self):
        m=self.b.build(CustomTopology("quad",((0,0,0),(1,0,0),(1,0,1),(0,0,1)),((0,1,2,3),)))
        self.assertEqual(m.triangles,((0,1,2),(0,2,3)))
        self.assertFalse(m.closed_oriented())

    def test_custom_closed(self):
        b=self.b.build(Box("cube",(1,2,3)))
        m=self.b.build(CustomTopology("custom",b.vertices,b.triangles,True))
        self.assertTrue(m.closed_oriented())
        self.assertAlmostEqual(m.signed_volume(),6)

    def test_custom_bowtie_and_fans(self):
        vs=((0,0,0),(1,0,0),(0,0,1),(-1,0,0),(0,0,-1))
        with self.assertRaises(ValueError):
            self.b.build(CustomTopology("fan",vs,((0,1,2),(0,3,4))))
        with self.assertRaises(ValueError):
            self.b.build(CustomTopology("cross",((0,0,0),(1,0,1),(1,0,0),(0,0,1)),((0,1,2,3),)))
        with self.assertRaises(ValueError):
            self.b.build(CustomTopology("open",vs[:3],((0,1,2),),True))

    def test_custom_bad_winding(self):
        with self.assertRaises(ValueError):
            self.b.build(CustomTopology("winding",((0,0,0),(1,0,0),(0,0,1),(0,1,0)),((0,1,2),(0,1,3))))

class OrganicBlenderTests(unittest.TestCase):
    def setUp(self):
        self.b=BlenderBackend()
        if not self.b.available:
            if os.environ.get("FRONTLINE_REQUIRE_BLENDER")=="1":
                self.fail("actual Blender required")
            self.skipTest("optional Blender absent")

    def test_patch_roundtrip(self):
        p=patch()
        a=PythonBackend().build(p)
        b=self.b.build(p)
        self.assertEqual(len(a.vertices),len(b.vertices))
        self.assertEqual(len(a.triangles),len(b.triangles))
        self.assertFalse(b.closed_oriented())
        for u,v in zip(a.bounds(),b.bounds()):
            for x,y in zip(u,v):
                self.assertAlmostEqual(x,y,places=6)

    def test_loft_roundtrip(self):
        p=loft()
        a=PythonBackend().build(p)
        b=self.b.build(p)
        self.assertTrue(b.closed_oriented())
        self.assertEqual(len(a.vertices),len(b.vertices))
        self.assertEqual(len(a.triangles),len(b.triangles))
        self.assertAlmostEqual(a.signed_volume(),b.signed_volume(),places=6)

if __name__=="__main__":
    unittest.main()
