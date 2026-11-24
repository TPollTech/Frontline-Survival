"""Analytical and real Blender rig tests, neutral articulated structure."""
import json
import math
import os
from pathlib import Path
import subprocess
import tempfile
import unittest
from tools.asset_pipeline.parametric import Box,PythonBackend,MeshSpec,NodeSpec,SceneSpec,Transform,BlenderBackend,build_render_mesh
from tools.asset_pipeline.parametric.rig import (BoneSpec,SkeletonSpec,SkinSpec,SocketSpec,RigSpec,
    inverse,rotation,around_pivot,reparent,attachment_local)

def fixture():
    mesh=MeshSpec("panel",((0,0,0),(1,1,0),(0,2,0)),((0,1,2),))
    skeleton=SkeletonSpec("skeleton",(BoneSpec("tip","root",Transform.translation((0,1,0)),1),
                                      BoneSpec("root",length_m=1)))
    skin=SkinSpec(mesh.id,skeleton.id,((("root",1),),(("root",0.5),("tip",0.5)),(("tip",1),)))
    return mesh,skeleton,skin

class RigTests(unittest.TestCase):
    def assertVector(self,a,b):
        for x,y in zip(a,b):
            self.assertAlmostEqual(x,y,places=7)

    def test_affine_inverse(self):
        t=Transform.translation((3,-2,1))@rotation((1,2,3),0.7)@Transform.scale((2,3,4))
        self.assertVector((inverse(t)@t).matrix,Transform().matrix)

    def test_pivot(self):
        t=around_pivot(rotation((0,0,1),math.pi/2),(1,2,0))
        self.assertVector(t.point((1,2,0)),(1,2,0))
        self.assertVector(t.point((2,2,0)),(1,3,0))

    def test_reparent_world_and_cycle(self):
        s=SceneSpec("scene",(),(),(NodeSpec("a",local=Transform.translation((1,0,0))),
            NodeSpec("b",local=rotation((0,1,0),0.6)),NodeSpec("c",parent_id="a",local=Transform.translation((0,2,0)))))
        changed=reparent(s,"c","b")
        self.assertVector(changed.world_transforms()["c"].matrix,s.world_transforms()["c"].matrix)
        self.assertEqual(reparent(s,"c","b",keep_world=False).nodes[-1].local,s.nodes[-1].local)
        with self.assertRaises(ValueError):
            reparent(s,"a","c")

    def test_attachment(self):
        p=Transform.translation((2,3,4))@rotation((0,1,0),0.7)
        t=Transform.translation((-2,0,4))@rotation((1,0,0),0.3)
        s=Transform.translation((0,0,0.4))@rotation((0,0,1),0.5)
        self.assertVector((p@attachment_local(p,t,s)@s).matrix,t.matrix)

    def test_skeleton_order_bind_and_pose(self):
        _,sk,_=fixture()
        self.assertEqual([b.id for b in sk.bones],["root","tip"])
        self.assertEqual(sk.transforms()["tip"].point((0,0,0)),(0,1,0))
        for k,t in sk.transforms().items():
            self.assertVector((t@sk.inverse_bind()[k]).matrix,Transform().matrix)
        p=sk.transforms({"root":rotation((0,0,1),math.pi/2)})
        self.assertVector(p["tip"].point((0,0,0)),(-1,0,0))

    def test_bad_skeleton(self):
        for bones in ((BoneSpec("a"),BoneSpec("b")),(BoneSpec("a"),BoneSpec("b","missing")),
            (BoneSpec("a"),BoneSpec("b","c"),BoneSpec("c","b")),(BoneSpec("a"),BoneSpec("a"))):
            with self.assertRaises(ValueError):
                SkeletonSpec("s",bones)
        with self.assertRaises(ValueError):
            BoneSpec("scaled",rest_local=Transform.scale((2,1,1)))

    def test_skin_rest_pose_and_blend(self):
        m,s,k=fixture()
        self.assertEqual(k.deform(m,s),m.vertices)
        result=k.deform(m,s,{"tip":rotation((0,0,1),math.pi/2)})
        for a,b in zip(result,((0,0,0),(0.5,1.5,0),(-1,1,0))):
            self.assertVector(a,b)

    def test_invalid_weights_and_pose(self):
        m,s,k=fixture()
        for weights in (((("root",0.2),),),((("root",1),("root",0)),),((("root",-1),("tip",2)),)):
            with self.assertRaises(ValueError):
                SkinSpec(m.id,s.id,weights)
        with self.assertRaises(ValueError):
            SkinSpec(m.id,s.id,((("missing",1),),)*3).validate(m,s)
        with self.assertRaises(ValueError):
            SkinSpec(m.id,s.id,((("root",1),),)).validate(m,s)
        with self.assertRaises(ValueError):
            s.transforms({"bad":Transform()})

    def test_render_weights(self):
        m,s,k=fixture()
        r=build_render_mesh(m)
        self.assertEqual(k.render_weights(r,s),tuple(k.weights[i] for i in r.source_vertices))

    def test_rig_sockets(self):
        m,s,k=fixture()
        scene=SceneSpec("scene",(m,),(),(NodeSpec("anchor",local=Transform.translation((2,0,0))),
            NodeSpec("panel",m.id,"anchor")))
        a=SocketSpec("node_socket","panel",local=Transform.translation((0,1,0)))
        b=SocketSpec("bone_socket","tip","bone",Transform.translation((0,1,0)))
        rig=RigSpec("rig",scene,s,"anchor",(k,),(a,b))
        self.assertVector(rig.socket_world("node_socket").point((0,0,0)),(2,1,0))
        self.assertVector(rig.socket_world("bone_socket",{"tip":rotation((0,0,1),math.pi/2)}).point((0,0,0)),(1,1,0))
        self.assertEqual(rig.sha256(),RigSpec("rig",scene,s,"anchor",(k,),(b,a)).sha256())
        with self.assertRaises(ValueError):
            RigSpec("rig",scene,s,"anchor",(k,),(SocketSpec("bad","unknown"),))

    def test_skin_bind_frame(self):
        m,s,k=fixture()
        scene=SceneSpec("scene",(m,),(),(NodeSpec("anchor"),NodeSpec("part",m.id,"anchor",local=Transform.translation((1,0,0)))))
        with self.assertRaises(ValueError):
            RigSpec("rig",scene,s,"anchor",(k,))

class BlenderRigTests(unittest.TestCase):
    def test_actual_armature_skin(self):
        backend=BlenderBackend()
        if not backend.available:
            if os.environ.get("FRONTLINE_REQUIRE_BLENDER")=="1":
                self.fail("actual Blender required")
            self.skipTest("optional Blender absent")
        m,s,k=fixture()
        # Nontrivial parent and child rotations test local vs world semantics.
        pose={"root":rotation((0,1,0),0.3),"tip":rotation((0,0,1),math.pi/2)}
        rest=s.transforms()
        data={"bones":[{"id":b.id,"parent_id":b.parent_id,"length_m":b.length_m,
                        "rest_world":rest[b.id].matrix,"delta":pose.get(b.id,Transform()).matrix} for b in s.bones],
              "vertices":m.vertices,"triangles":m.triangles,"weights":k.weights}
        with tempfile.TemporaryDirectory() as d:
            src,dst=Path(d)/"input.json",Path(d)/"output.json"
            src.write_text(json.dumps(data))
            script=Path(__file__).resolve().parents[1]/"tools/asset_pipeline/parametric/rig_bridge.py"
            proc=subprocess.run([backend.executable,"--background","--factory-startup","--disable-autoexec","--python-exit-code","1","--python",str(script),"--",str(src),str(dst)],capture_output=True,text=True,timeout=120)
            self.assertEqual(proc.returncode,0,msg=proc.stdout+proc.stderr)
            result=json.loads(dst.read_text())
            self.assertTrue(result["version"])
            self.assertEqual(len(result["vertices"]),len(m.vertices))
            for a,b in zip(result["vertices"],k.deform(m,s,pose)):
                for x,y in zip(a,b):
                    self.assertAlmostEqual(x,y,places=5)
            for name,t in s.transforms(pose).items():
                for x,y in zip(result["pose_world"][name],t.matrix):
                    self.assertAlmostEqual(x,y,places=5)

if __name__=="__main__":
    unittest.main()
