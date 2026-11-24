import math
import unittest
from dataclasses import replace
from tools.asset_pipeline.parametric import Box,Cylinder,PythonBackend,Transform,NodeSpec,SceneSpec,MeshSpec,Extrusion
from tools.asset_pipeline.parametric.lod import (BUDGETS,NON_GEOMETRY_CATEGORIES,CategoryBudget,ColliderSpec,LODLevel,AssetLOD,
    resample_recipe,build_single_recipe_lods)
from tools.asset_pipeline.parametric.rig import rotation

def fixture():
    return build_single_recipe_lods(Cylinder("column",0.5,2,64),"object",
        colliders=(ColliderSpec("proxy","root","capsule",dimensions_m=(0.5,2)),))

class LODTests(unittest.TestCase):
    def test_recipe_levels(self):
        a=fixture()
        self.assertEqual([l.metrics()["triangles"] for l in a.levels],[256,128,64])
        self.assertEqual([l.metrics()["render_vertex_upper_bound"] for l in a.levels],[768,384,192])
        self.assertEqual(a.sha256(),fixture().sha256())
        self.assertEqual(a.levels[0].scene.world_bounds(),a.levels[2].scene.world_bounds())
        self.assertEqual(len(a.colliders),1)

    def test_hysteresis(self):
        a=fixture()
        self.assertEqual([a.select(d) for d in (0,11.9,12,29.9,30,500)],[0,0,1,1,2,2])
        self.assertEqual(a.select(12.5,0),0)
        self.assertEqual(a.select(13,0),1)
        self.assertEqual(a.select(11.5,1),1)
        self.assertEqual(a.select(10.9,1),0)
        self.assertEqual(a.select(100,0),2)
        self.assertEqual(a.select(0,2),0)

    def test_collider_bounds(self):
        c=ColliderSpec("box","root","box",dimensions_m=(2,4,6))
        self.assertEqual(c.local_bounds(),((-1,-2,-3),(1,2,3)))
        c=ColliderSpec("sphere","root","sphere",dimensions_m=(2,))
        self.assertEqual(c.local_bounds(),((-2,-2,-2),(2,2,2)))
        self.assertEqual(fixture().colliders[0].local_bounds(),((-0.5,-1,-0.5),(0.5,1,0.5)))

    def test_convex_and_static_mesh(self):
        m=PythonBackend().build(Box("proxy",(1,1,1)))
        ColliderSpec("convex","root","convex",proxy=m,body="dynamic")
        plane=MeshSpec("floor",((0,0,0),(1,0,0),(0,0,1)),((0,2,1),))
        ColliderSpec("floor","root","concave",proxy=plane)
        with self.assertRaises(ValueError):
            ColliderSpec("floor","root","concave",proxy=plane,body="dynamic")
        concave=PythonBackend().build(Extrusion("l",((0,0),(2,0),(2,1),(1,1),(1,2),(0,2)),1))
        with self.assertRaises(ValueError):
            ColliderSpec("bad","root","convex",proxy=concave)

    def test_invalid_shapes(self):
        for kind,d in (("box",(1,0,1)),("capsule",(1,1)),("sphere",(-1,)),("unknown",(1,))):
            with self.assertRaises(ValueError):
                ColliderSpec("bad","root",kind,dimensions_m=d)
        with self.assertRaises(ValueError):
            ColliderSpec("bad","root","box",Transform.scale((2,1,1)),(1,1,1))

    def test_collision_independent(self):
        a=fixture()
        c=ColliderSpec("proxy","root","convex",proxy=a.levels[0].scene.meshes[0])
        with self.assertRaises(ValueError):
            replace(a,colliders=(c,))
        with self.assertRaises(ValueError):
            replace(a,colliders=(replace(a.colliders[0],owner_node_id="missing"),))
        with self.assertRaises(ValueError):
            replace(a,colliders=tuple(replace(a.colliders[0],id=f"c{i}") for i in range(9)))

    def test_collision_transform_invariant(self):
        a=fixture()
        t=Transform.translation((2,3,4))@rotation((0,1,0),0.7)
        levels=tuple(replace(l,scene=replace(l.scene,nodes=(replace(l.scene.nodes[0],local=t),))) for l in a.levels)
        c=replace(a.colliders[0],local=Transform.translation((0,1,0)))
        a=replace(a,levels=levels,colliders=(c,))
        self.assertEqual(a.collision_world("proxy").point((0,0,0)),(2,4,4))
        self.assertEqual(a.select(100),2)

    def test_invalid_lod(self):
        a=fixture()
        with self.assertRaises(ValueError):
            replace(a,levels=(a.levels[0],replace(a.levels[1],scene=a.levels[0].scene),a.levels[2]))
        with self.assertRaises(ValueError):
            replace(a,levels=(a.levels[0],replace(a.levels[1],start_distance_m=0),a.levels[2]))
        with self.assertRaises(ValueError):
            replace(a,category="audio")
        with self.assertRaises(ValueError):
            replace(a,levels=(a.levels[0],replace(a.levels[1],scene=replace(a.levels[1].scene,nodes=(replace(a.levels[1].scene.nodes[0],local=Transform.translation((1,0,0))),))),a.levels[2]))

    def test_budget_and_bounds(self):
        a=fixture()
        with self.assertRaises(ValueError):
            build_single_recipe_lods(Cylinder("big",1,2,512),"effect")
        l=a.levels[2]
        m=PythonBackend().build(Cylinder("small",0.1,2,16))
        l=replace(l,scene=replace(l.scene,meshes=(m,),nodes=(NodeSpec("root",m.id),)))
        with self.assertRaises(ValueError):
            replace(a,levels=(a.levels[0],a.levels[1],l))

    def test_budget_schema(self):
        with self.assertRaises(ValueError):
            CategoryBudget((1,2,3),1,1,1)
        self.assertEqual(len(BUDGETS),13)
        self.assertFalse(set(BUDGETS)&NON_GEOMETRY_CATEGORIES)
        with self.assertRaises(ValueError):
            resample_recipe(Box("box",(1,1,1)),1)

if __name__=="__main__":
    unittest.main()
