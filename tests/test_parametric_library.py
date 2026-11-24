"""Neutral technical fixtures; no production game asset is edited."""
import math
import os
import unittest
from tools.asset_pipeline.parametric import (
    Box, Cylinder, PythonBackend, BlenderBackend, BlenderError, MeshSpec,
    MaterialSpec, NodeSpec, SceneSpec, Transform)
from tools.asset_pipeline.parametric.model import blender_to_canonical, canonical_to_blender

class ParametricTests(unittest.TestCase):
    def setUp(self):
        self.backend=PythonBackend()
        self.box=self.backend.build(Box("fixture_box",(2,3,4)))

    def test_box_dimensions(self):
        self.assertEqual(self.box.bounds(),((-1,-1.5,-2),(1,1.5,2)))
        self.assertEqual(len(self.box.triangles),12)

    def test_box_topology(self):
        self.assertTrue(self.box.closed_oriented())
        self.assertAlmostEqual(self.box.signed_volume(),24)

    def test_cylinder_topology(self):
        m=self.backend.build(Cylinder("fixture_cylinder",0.5,2,32))
        self.assertTrue(m.closed_oriented())
        self.assertEqual(len(m.vertices),66)
        self.assertEqual(len(m.triangles),128)
        self.assertAlmostEqual(m.signed_volume(),32*0.5*0.25*math.sin(math.tau/32)*2)
        self.assertAlmostEqual(m.bounds()[0][1],-1)

    def test_bad_dimensions(self):
        for dims in [(0,1,1),(-1,1,1),(1,math.inf,1),(True,1,1),(1,2)]:
            with self.subTest(dims=dims),self.assertRaises(ValueError):
                Box("box",dims)

    def test_bad_segments(self):
        for seg in [2,513,3.5,True]:
            with self.subTest(seg=seg),self.assertRaises(ValueError):
                Cylinder("c",1,1,seg)

    def test_invalid_index(self):
        with self.assertRaises(ValueError):
            MeshSpec("bad",((0,0,0),(1,0,0),(0,1,0)),((0,1,9),))

    def test_degenerate(self):
        with self.assertRaises(ValueError):
            MeshSpec("bad",((0,0,0),(1,0,0),(2,0,0)),((0,1,2),))

    def test_duplicate_face(self):
        with self.assertRaises(ValueError):
            MeshSpec("bad",((0,0,0),(1,0,0),(0,1,0)),((0,1,2),(2,1,0)))

    def test_unused_vertex(self):
        with self.assertRaises(ValueError):
            MeshSpec("bad",((0,0,0),(1,0,0),(0,1,0),(0,0,1)),((0,1,2),))

    def test_material_range(self):
        with self.assertRaises(ValueError):
            MaterialSpec("bad",metallic=1.1)

    def test_affine_composition(self):
        a=Transform.translation((2,3,4))@Transform.scale((2,3,4))
        self.assertEqual(a.point((1,1,1)),(4,6,8))

    def test_singular_matrix(self):
        with self.assertRaises(ValueError):
            Transform.scale((0,1,1))

    def test_reflection(self):
        with self.assertRaises(ValueError):
            Transform((-1,0,0,0,0,1,0,0,0,0,1,0,0,0,0,1))

    def test_basis(self):
        self.assertEqual(blender_to_canonical((0,0,1)),(0,1,0))
        self.assertEqual(blender_to_canonical((0,1,0)),(0,0,-1))
        v=(1.25,-2.5,3.75)
        self.assertEqual(blender_to_canonical(canonical_to_blender(v)),v)

    def scene(self, reverse=False):
        nodes=[NodeSpec("parent",local=Transform.translation((1,2,3))),
               NodeSpec("part",self.box.id,"parent","mat",Transform.translation((0,2,0)))]
        if reverse:
            nodes.reverse()
        return SceneSpec("fixture",(self.box,),(MaterialSpec("mat"),),nodes)

    def test_hierarchy_and_world_bounds(self):
        s=self.scene()
        self.assertEqual(s.world_transforms()["part"].point((0,0,0)),(1,4,3))
        self.assertEqual(s.world_bounds(),((0,2.5,1),(2,5.5,5)))

    def test_deterministic_ir(self):
        self.assertEqual(self.scene().canonical_json(),self.scene(True).canonical_json())
        self.assertEqual(self.scene().sha256(),self.scene(True).sha256())

    def test_missing_reference(self):
        with self.assertRaises(ValueError):
            SceneSpec("s",(),(),(NodeSpec("n","missing"),))

    def test_cycle(self):
        with self.assertRaises(ValueError):
            SceneSpec("s",(),(),(NodeSpec("a",parent_id="b"),NodeSpec("b",parent_id="a")))

    def test_duplicate_id(self):
        with self.assertRaises(ValueError):
            SceneSpec("s",(),(),(NodeSpec("a"),NodeSpec("a")))

    def test_backend_missing(self):
        with self.assertRaises(BlenderError):
            BlenderBackend(executable="/nonexistent/frontline/blender").build(Box("b",(1,2,3)))

class BlenderIntegrationTests(unittest.TestCase):
    def setUp(self):
        self.backend=BlenderBackend()
        if not self.backend.available:
            if os.environ.get("FRONTLINE_REQUIRE_BLENDER")=="1":
                self.fail("Blender is required in this job")
            self.skipTest("optional Blender executable absent")

    def test_asymmetric_roundtrip(self):
        expected=PythonBackend().build(Box("asymmetric",(0.5,1.25,2.75)))
        shifted=MeshSpec(expected.id,[(x+0.125,y-0.25,z+0.75) for x,y,z in expected.vertices],expected.triangles)
        actual=self.backend.evaluate(shifted)
        self.assertEqual(len(actual.triangles),12)
        self.assertTrue(actual.closed_oriented())
        for a,b in zip(actual.bounds(),shifted.bounds()):
            for x,y in zip(a,b):
                self.assertAlmostEqual(x,y,places=6)
        self.assertAlmostEqual(actual.signed_volume(),shifted.signed_volume(),places=6)
        # Compare positions in each oriented triangle, independent of starting index.
        def faces(mesh):
            def cycle(face):
                points=tuple(tuple(round(v,6) for v in mesh.vertices[i]) for i in face)
                return min(points[i:]+points[:i] for i in range(3))
            return sorted(cycle(face) for face in mesh.triangles)
        self.assertEqual(faces(actual),faces(shifted))

    def test_actual_blender_bevel(self):
        m=PythonBackend().build(Box("bevel_fixture",(1,2,3)))
        b=self.backend.evaluate(m,bevel_m=0.04,segments=2)
        self.assertTrue(b.closed_oriented())
        self.assertGreater(len(b.triangles),len(m.triangles))
        self.assertLess(b.signed_volume(),m.signed_volume())
        for a,c in zip(b.bounds(),m.bounds()):
            for x,y in zip(a,c):
                self.assertAlmostEqual(x,y,places=5)

if __name__=="__main__":
    unittest.main()
