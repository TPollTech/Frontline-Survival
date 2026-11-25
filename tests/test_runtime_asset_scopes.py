import unittest
from tools.asset_pipeline.runtime_asset_scopes import scope_rows, scope_evidence


def mesh(path):
    return {"path": path, "mesh": {"surfaces": []}, "visible_in_tree": True}


def shot():
    return {"id": "combat_visual_event", "families": ["effect:combat"],
            "nodes": [{"path": "."}, mesh("Map"), mesh("Map/Extra"), mesh("Tracer"), mesh("Casing"), mesh("Impact")],
            "asset_scopes": [{"role": "shot_fx", "roots": ["Tracer", "Casing", "Impact"]}]}


def player():
    return {"id": "fps_rifle___hip", "families": ["player:collision", "effect:muzzle", "effect:scope_overlay"],
            "nodes": [{"path": ".", "class": "CharacterBody3D", "collision_layer": 2, "collision_mask": 1},
                      {"path": "Collider", "collision": {"class": "CapsuleShape3D"}}, mesh("Muzzle"),
                      {"path": "Scope", "canvas_material": {"shader": "res://scripts/scope.gdshader"}, "canvas_visible_in_tree": False}],
            "asset_scopes": [{"role": "player_capsule", "roots": ["Collider"]},
                             {"role": "muzzle_mesh", "roots": ["Muzzle"]}, {"role": "scope_canvas", "roots": ["Scope"]}]}


class RuntimeScopesTests(unittest.TestCase):
    def test_only_new_effect_nodes(self):
        row = scope_rows(shot())[0]
        self.assertEqual(row["node_paths"], ["Casing", "Impact", "Tracer"])
        self.assertEqual(row["mesh_nodes"], 3)
        self.assertFalse(row["approved"])

    def test_wrong_whole_scene_scope(self):
        data = shot(); data["asset_scopes"][0]["roots"] = ["."]
        with self.assertRaisesRegex(ValueError, "component count"): scope_rows(data)

    def test_unknown_path(self):
        data = shot(); data["asset_scopes"][0]["roots"][0] = "Fake"
        with self.assertRaisesRegex(ValueError, "invalid scope roots"): scope_rows(data)

    def test_overlapping_paths(self):
        data = shot(); data["asset_scopes"][0]["roots"] = ["Map", "Map/Extra"]
        with self.assertRaisesRegex(ValueError, "overlapping roots"): scope_rows(data)

    def test_missing_role(self):
        data = player(); data["asset_scopes"].pop()
        with self.assertRaisesRegex(ValueError, "scope roles"): scope_rows(data)

    def test_collision_and_canvas(self):
        rows = scope_rows(player())
        self.assertEqual(rows[0]["collisions"][0]["layer"], 2)
        self.assertFalse(rows[2]["canvas_visible"])
        self.assertEqual(rows[2]["mesh_nodes"], 0)

    def test_wrong_collision_layer(self):
        data = player(); data["nodes"][0]["collision_layer"] = 8
        with self.assertRaisesRegex(ValueError, "collision layers"): scope_rows(data)

    def test_wrong_shader(self):
        data = player(); data["nodes"][3]["canvas_material"]["shader"] = "fake"
        with self.assertRaisesRegex(ValueError, "shader identity"): scope_rows(data)

    def test_old_and_incomplete_capture(self):
        self.assertEqual(scope_evidence({"samples": [shot()]}), {})
        with self.assertRaisesRegex(ValueError, "incomplete scoped runtime roles"):
            scope_evidence({"asset_scope_schema": 1, "samples": [shot()]})


if __name__ == "__main__":
    unittest.main()
