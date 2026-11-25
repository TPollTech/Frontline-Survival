"""Ensure runtime category limits do not silently diverge from the canonical IR."""
import pathlib,re,unittest
from tools.asset_pipeline.parametric.lod import BUDGETS
class WorldLODContract(unittest.TestCase):
    def test_runtime_structure_budget(self):
        root=pathlib.Path(__file__).resolve().parents[1]
        source=(root/"scripts/world_lod.gd").read_text()
        b=BUDGETS["structure"]
        self.assertEqual(tuple(map(int,re.search(r"TRIANGLE_CAPS := \[([0-9,]+)\]",source)[1].split(","))),b.triangles)
        self.assertEqual(int(re.search(r"COLLIDER_CAP := (\d+)",source)[1]),b.max_colliders)
        self.assertEqual(int(re.search(r"MATERIAL_CAP := (\d+)",source)[1]),b.max_material_slots)
    def test_runtime_object_budget(self):
        source=(pathlib.Path(__file__).resolve().parents[1]/"scripts/world_lod.gd").read_text()
        b=BUDGETS["object"]
        self.assertEqual(tuple(map(int,re.search(r"OBJECT_TRIANGLE_CAPS := \[([0-9,]+)\]",source)[1].split(","))),b.triangles)
        self.assertEqual(int(re.search(r"OBJECT_COLLIDER_CAP := (\d+)",source)[1]),b.max_colliders)
        self.assertEqual(int(re.search(r"OBJECT_MATERIAL_CAP := (\d+)",source)[1]),b.max_material_slots)
if __name__=="__main__":unittest.main()
