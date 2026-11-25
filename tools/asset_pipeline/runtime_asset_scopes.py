"""Validate QA-selected actual node scopes, never fabricate geometry or approval."""
from collections import defaultdict

# role -> (historical family, exact mesh count or None, collider count, light count)
SPECS = {
    "player_capsule": ("player:collision", 0, 1, 0),
    "muzzle_mesh": ("effect:muzzle", 1, 0, 0),
    "scope_canvas": ("effect:scope_overlay", 0, 0, 0),
    "turret": ("object:turret", 2, 0, 1),
    "loot_weapon": ("object:loot", None, 0, 0),
    "loot_ammo": ("object:loot", 2, 0, 0),
    "grenade_body": ("object:grenade", 3, 1, 0),
    "grenade_fx": ("effect:grenade", 24, 0, 1),
    "blood": ("effect:blood", 7, 0, 0),
    "shot_fx": ("effect:combat", 3, 0, 0),
    "enemy_tracer": ("effect:enemy_tracer", 1, 0, 0),
    "airstrike_marker": ("effect:combat", 1, 0, 0),
    "airstrike_impact": ("effect:combat", 1, 0, 0),
}


def require(ok, message):
    if not ok:
        raise ValueError(message)


def expected_roles(sample_id):
    if sample_id.startswith("fps_"):
        return {"player_capsule", "muzzle_mesh", "scope_canvas"}
    if sample_id.startswith("loot_weapon_"):
        return {"loot_weapon"}
    return {"turret": {"turret"}, "loot_ammo": {"loot_ammo"},
            "grenade": {"grenade_body"}, "grenade_effect": {"grenade_fx"},
            "blood_effect": {"blood"}, "combat_visual_event": {"shot_fx"},
            "enemy_tracer": {"enemy_tracer"}, "airstrike_marker": {"airstrike_marker"},
            "airstrike_impact": {"airstrike_impact"}}.get(sample_id, set())


def scope_rows(sample):
    scopes = sample.get("asset_scopes", [])
    roles = [s["role"] for s in scopes]
    require(len(roles) == len(set(roles)) and set(roles) == expected_roles(sample["id"]), "scope roles: " + sample["id"])
    nodes = {n["path"]: n for n in sample["nodes"]}
    require(len(nodes) == len(sample["nodes"]), "duplicate node path")
    result = []
    for scope in scopes:
        role = scope["role"]
        family, mesh_count, collider_count, light_count = SPECS[role]
        require(family in sample["families"], "scope family absent: " + family)
        roots = scope["roots"]
        require(isinstance(roots, list) and roots and len(set(roots)) == len(roots) and all(p in nodes for p in roots), "invalid scope roots: " + role)
        chosen = set()
        for root in roots:
            paths = {p for p in nodes if root == "." or p == root or p.startswith(root + "/")}
            require(not chosen.intersection(paths), "overlapping roots: " + role)
            chosen.update(paths)
        rows = [nodes[p] for p in sorted(chosen)]
        meshes = [n for n in rows if n.get("mesh") and not n["mesh"].get("missing")]
        shapes = [n for n in rows if n.get("collision") and not n["collision"].get("missing")]
        lights = [n for n in rows if n.get("light")]
        require((len(meshes) > 0 if mesh_count is None else len(meshes) == mesh_count) and len(shapes) == collider_count and len(lights) == light_count, "scope component count: " + role)
        collisions = []
        for n in shapes:
            parent = n["path"].rpartition("/")[0] or "."
            body = nodes.get(parent, {})
            require(body.get("class") == ("CharacterBody3D" if role == "player_capsule" else "RigidBody3D"), "collision parent: " + role)
            require(n["collision"].get("class") == ("CapsuleShape3D" if role == "player_capsule" else "SphereShape3D"), "collision shape: " + role)
            require(body.get("collision_layer") == (2 if role == "player_capsule" else 8) and body.get("collision_mask") == 1, "collision layers: " + role)
            collisions.append({"path": n["path"], "body": parent, "shape": n["collision"],
                               "layer": body["collision_layer"], "mask": body["collision_mask"]})
        if role == "scope_canvas":
            require(len(rows) == 1 and rows[0].get("canvas_material", {}).get("shader") == "res://scripts/scope.gdshader", "scope shader identity")
        if role in ("muzzle_mesh", "player_capsule", "scope_canvas"):
            require(len(roots) == len(rows) == 1, "single component scope: " + role)
        result.append({"family": family, "sample": sample["id"], "role": role,
                       "roots": roots, "node_paths": sorted(chosen), "mesh_nodes": len(meshes),
                       "collisions": collisions, "lights": len(lights),
                       "visible_mesh_nodes": sum(n.get("visible_in_tree") is True for n in meshes),
                       "canvas_visible": rows[0].get("canvas_visible_in_tree") if role == "scope_canvas" else None,
                       "scope": "qa_selected_actual_nodes", "approved": False})
    return result


def scope_evidence(runtime):
    if "asset_scope_schema" not in runtime:
        return {}  # Older inventories lack exact scopes; no inferred ownership.
    require(runtime["asset_scope_schema"] == 1, "unknown asset scope schema")
    result = defaultdict(list)
    seen_roles = set()
    for sample in runtime["samples"]:
        for row in scope_rows(sample):
            seen_roles.add(row["role"])
            result[row["family"]].append(row)
    require(seen_roles == set(SPECS), "incomplete scoped runtime roles")
    return dict(sorted(result.items()))
