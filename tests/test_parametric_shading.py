"""Shading tests on neutral geometry, including actual Blender MikkTSpace."""
import math
import os
import unittest
from tools.asset_pipeline.parametric import Box, PythonBackend, MeshSpec, BlenderBackend
from tools.asset_pipeline.parametric.shading import (
    corner_normals, planar_uv, triangle_atlas_uv, corner_tangents, build_render_mesh, RenderMesh)
from tools.asset_pipeline.parametric.shading_blender import blender_tangents
from tools.asset_pipeline.parametric.model import dot

def plane():
    return MeshSpec("plane",((0,0,0),(1,0,0),(1,1,0),(0,1,0)),((0,1,2),(0,2,3)))

def uv_plane(mesh):
    return planar_uv(mesh,u_axis=(1,0,0),v_axis=(0,1,0))

class ShadingTests(unittest.TestCase):
    def test_planar_normals(self):
        m=plane()
        for w in ("uniform","area","angle","area_angle"):
            self.assertEqual(corner_normals(m,weighting=w),((0,0,1),)*6)

    def test_cube_hard_edges(self):
        m=PythonBackend().build(Box("box",(2,2,2)))
        ns=corner_normals(m,crease_rad=math.pi/4)
        self.assertEqual(len(set(ns)),6)
        for i in range(0,len(ns),3):
            self.assertEqual(ns[i],ns[i+1])
            self.assertEqual(ns[i],ns[i+2])

    def test_smooth_cube(self):
        m=PythonBackend().build(Box("box",(2,2,2)))
        ns=corner_normals(m,weighting="angle",crease_rad=math.pi)
        for v,n in zip((i for f in m.triangles for i in f),ns):
            for a,b in zip(m.vertices[v],n):
                self.assertAlmostEqual(b,a/math.sqrt(3))

    def test_weighted_normals(self):
        m=MeshSpec("corner",((0,0,0),(1,0,0),(0,2,0),(0,0,1)),((0,1,2),(1,0,3)))
        a=corner_normals(m,weighting="area",crease_rad=math.pi)
        self.assertAlmostEqual(a[0][2],2/math.sqrt(5))
        self.assertAlmostEqual(a[0][1],1/math.sqrt(5))
        b=corner_normals(m,weighting="uniform",crease_rad=math.pi)
        self.assertAlmostEqual(b[0][2],1/math.sqrt(2))
        c=corner_normals(m,crease_rad=math.pi,sharp_edges=((0,1),))
        self.assertEqual(c[0],(0,0,1))
        self.assertEqual(c[4],(0,1,0))

    def test_atlas_padding_and_separation(self):
        m=PythonBackend().build(Box("box",(1,2,3)))
        uv=triangle_atlas_uv(m)
        side=math.ceil(math.sqrt(len(m.triangles)))
        for f in range(len(m.triangles)):
            for u,v in uv[3*f:3*f+3]:
                self.assertEqual((int(u*side),int(v*side)),(f%side,f//side))
                self.assertTrue(0<u<1 and 0<v<1)
        self.assertEqual(uv,triangle_atlas_uv(m))

    def test_render_plane(self):
        m=plane()
        r=build_render_mesh(m,uv=uv_plane(m))
        self.assertEqual(len(r.positions),4)
        self.assertEqual(r.tangents,((1,0,0,1),)*4)
        self.assertEqual(r.mesh,m)
        self.assertEqual(r,build_render_mesh(m,uv=uv_plane(m)))

    def test_mirrored_uv(self):
        m=plane()
        uv=tuple((-u,v) for u,v in uv_plane(m))
        r=build_render_mesh(m,uv=uv)
        self.assertEqual(r.tangents,((-1,0,0,-1),)*4)

    def test_seam_and_mirror_split(self):
        m=plane()
        uv=((0,0),(1,0),(1,1),(0,0),(1,1),(1,0))
        r=build_render_mesh(m,uv=uv)
        self.assertEqual(len(r.positions),6)
        self.assertEqual({t[3] for t in r.tangents},{-1.,1.})
        self.assertEqual(tuple(r.source_vertices[i] for i in r.indices),(0,1,2,0,2,3))

    def test_invalid_inputs(self):
        m=plane()
        for uv in (((0,0),)*6,((0,0),)*5,((math.nan,0),)*6):
            with self.assertRaises(ValueError):
                build_render_mesh(m,uv=uv)
        with self.assertRaises(ValueError):
            corner_normals(m,sharp_edges=((1,3),))
        with self.assertRaises(ValueError):
            planar_uv(m,u_axis=(1,0,0),v_axis=(1,0,0))

    def test_render_invariants(self):
        m=plane()
        r=build_render_mesh(m,uv=uv_plane(m))
        with self.assertRaises(ValueError):
            RenderMesh(m,r.positions,r.normals,r.uv,((0,0,1,1),)*4,r.indices,r.source_vertices)

class BlenderShadingTests(unittest.TestCase):
    def setUp(self):
        self.backend=BlenderBackend()
        if not self.backend.available:
            if os.environ.get("FRONTLINE_REQUIRE_BLENDER")=="1":
                self.fail("actual Blender required")
            self.skipTest("optional Blender absent")

    def test_mikk_planar_and_mirrored(self):
        m=plane()
        for sign in (1,-1):
            uv=tuple((u*sign,v) for u,v in uv_plane(m))
            r=build_render_mesh(m,uv=uv,tangent_backend=blender_tangents)
            for t in r.tangents:
                self.assertAlmostEqual(t[0],sign,places=5)
                self.assertAlmostEqual(t[1],0,places=5)
                self.assertEqual(t[3],sign)

    def test_mikk_cube_atlas(self):
        m=PythonBackend().build(Box("box",(1,2,3)))
        r=build_render_mesh(m,tangent_backend=blender_tangents)
        self.assertEqual(len(r.indices),36)
        self.assertEqual(len(r.positions),36)
        for n,t in zip(r.normals,r.tangents):
            self.assertAlmostEqual(dot(n,t[:3]),0,places=6)

if __name__=="__main__":
    unittest.main()
