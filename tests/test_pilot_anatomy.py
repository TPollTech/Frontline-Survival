import unittest,math
from tools.asset_pipeline.parametric.pilot_suite import PILOTS,authored_contract,mesh_for
from tools.asset_pipeline.parametric.pilot_anatomy import make_rig
from tools.asset_pipeline.parametric.pilot_finish import finished_library
from tools.asset_pipeline.parametric.rig import rotation
class AnatomyTests(unittest.TestCase):
    def test_both_rigs_all_lods(self):
        lib=finished_library(32)
        for name in ("glove","mannequin"):
            _,parts,_=PILOTS[name];contract,lo,hi=authored_contract(parts)
            for level in range(3):
                with self.subTest(name=name,level=level):
                    scene,rig,meta=make_rig(name,parts,tuple(mesh_for(p,level,name) for p in parts),lib,contract["pivots_local_m"])
                    self.assertGreater(meta["bone_count"],10);self.assertGreater(meta["mixed_vertices"],0)
                    self.assertEqual(meta["parents"][meta["pose_child"]],meta["pose_bone"])
                    before=rig.skeleton.transforms()[meta["pose_child"]].matrix[12:15]
                    pose={meta["pose_bone"]:rotation((1,0,0),math.radians(25))}
                    after=rig.skeleton.transforms(pose)[meta["pose_child"]].matrix[12:15]
                    self.assertGreater(math.dist(before,after),.001)
                    moved=0
                    for skin,mesh in zip(rig.skins,sorted(scene.meshes,key=lambda m:m.id)):
                        rest=skin.deform(mesh,rig.skeleton)
                        for a,b in zip(rest,mesh.vertices):self.assertLess(math.dist(a,b),1e-7)
                        deformed=skin.deform(mesh,rig.skeleton,pose)
                        moved+=sum(math.dist(a,b)>1e-5 for a,b in zip(rest,deformed))
                    self.assertGreater(moved,0)
if __name__=="__main__":unittest.main()
