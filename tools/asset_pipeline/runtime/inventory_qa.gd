extends SceneTree
## QA only: instantiate actual game recipes, inventory their nodes, never replace meshes.
const IDS: Array[String] = ["pistol", "smg", "rifle", "shotgun", "lmg", "sentinela", "sniper", "bolt_sniper"]
const Loot = preload("res://scripts/loot_pickup.gd")
const Grenade = preload("res://scripts/frag_grenade.gd")
const Blood = preload("res://scripts/blood_impact.gd")
var samples: Array[Dictionary] = []
var failures: Array[String] = []
var output_dir: String

func _initialize() -> void:
    call_deferred("_run")

func _expect(ok: bool, label: String) -> void:
    if not ok:
        failures.append(label)
        push_error("ASSET_RUNTIME_ERROR: " + label)

func _vec(v: Vector3) -> Array:
    return [v.x, v.y, v.z]

func _color(c: Color) -> Array:
    return [c.r, c.g, c.b, c.a]

func _matrix(t: Transform3D) -> Array:
    return [t.basis.x.x, t.basis.x.y, t.basis.x.z, 0.0,
        t.basis.y.x, t.basis.y.y, t.basis.y.z, 0.0,
        t.basis.z.x, t.basis.z.y, t.basis.z.z, 0.0,
        t.origin.x, t.origin.y, t.origin.z, 1.0]

func _texture(t: Texture2D) -> Variant:
    if t == null:
        return null
    return {"path": t.resource_path, "width": t.get_width(), "height": t.get_height()}

func _material(m: Material) -> Variant:
    if m == null:
        return null
    var result: Dictionary = {"class": m.get_class(), "path": m.resource_path}
    if m is StandardMaterial3D:
        var mat := m as StandardMaterial3D
        result.merge({"albedo": _color(mat.albedo_color), "metallic": mat.metallic,
            "roughness": mat.roughness, "transparency": mat.transparency,
            "cull_mode": mat.cull_mode, "shading_mode": mat.shading_mode,
            "vertex_color_as_albedo": mat.vertex_color_use_as_albedo,
            "triplanar": mat.uv1_triplanar, "uv_scale": _vec(mat.uv1_scale),
            "albedo_texture": _texture(mat.albedo_texture),
            "normal_texture": _texture(mat.normal_texture),
            "normal_enabled": mat.normal_enabled, "normal_scale": mat.normal_scale,
            "metallic_texture": _texture(mat.metallic_texture),
            "roughness_texture": _texture(mat.roughness_texture),
            "emission_enabled": mat.emission_enabled, "emission": _color(mat.emission)})
    elif m is ShaderMaterial:
        var shader_mat := m as ShaderMaterial
        result["shader"] = shader_mat.shader.resource_path if shader_mat.shader != null else ""
    return result

func _mesh(node: MeshInstance3D) -> Dictionary:
    if node.mesh == null:
        return {"missing": true}
    var mesh: Mesh = node.mesh
    var bounds: AABB = mesh.get_aabb()
    var surfaces: Array[Dictionary] = []
    for i in range(mesh.get_surface_count()):
        var arrays: Array = mesh.surface_get_arrays(i)
        var vertices: int = 0
        var indices: int = 0
        var normals: int = 0
        var uvs: int = 0
        if arrays.size() == Mesh.ARRAY_MAX:
            if arrays[Mesh.ARRAY_VERTEX] != null:
                vertices = arrays[Mesh.ARRAY_VERTEX].size()
            if arrays[Mesh.ARRAY_INDEX] != null:
                indices = arrays[Mesh.ARRAY_INDEX].size()
            if arrays[Mesh.ARRAY_NORMAL] != null:
                normals = arrays[Mesh.ARRAY_NORMAL].size()
            if arrays[Mesh.ARRAY_TEX_UV] != null:
                uvs = arrays[Mesh.ARRAY_TEX_UV].size()
        var primitive: int = mesh.surface_get_primitive_type(i)
        surfaces.append({"index": i, "primitive": primitive, "vertices": vertices,
            "indices": indices, "normals": normals, "uvs": uvs,
            "triangles": int((indices if indices > 0 else vertices) / 3.0) if primitive == Mesh.PRIMITIVE_TRIANGLES else null,
            "effective_material": _material(node.get_active_material(i))})
    return {"class": mesh.get_class(), "path": mesh.resource_path,
        "bounds_local_m": {"origin": _vec(bounds.position), "size": _vec(bounds.size)},
        "surfaces": surfaces, "lod_bias": node.lod_bias,
        "visibility_range_begin": node.visibility_range_begin,
        "visibility_range_end": node.visibility_range_end,
        "skin_path": node.skin.resource_path if node.skin != null else null,
        "skeleton_path": str(node.skeleton)}

func _shape(node: CollisionShape3D) -> Dictionary:
    var shape: Shape3D = node.shape
    if shape == null:
        return {"missing": true}
    var data: Dictionary = {"class": shape.get_class(), "disabled": node.disabled, "path": shape.resource_path}
    if shape is BoxShape3D:
        data["size_m"] = _vec((shape as BoxShape3D).size)
    elif shape is CapsuleShape3D:
        data["radius_m"] = (shape as CapsuleShape3D).radius
        data["height_m"] = (shape as CapsuleShape3D).height
    elif shape is CylinderShape3D:
        data["radius_m"] = (shape as CylinderShape3D).radius
        data["height_m"] = (shape as CylinderShape3D).height
    elif shape is SphereShape3D:
        data["radius_m"] = (shape as SphereShape3D).radius
    return data

func _walk(node: Node, origin: Node, rows: Array[Dictionary]) -> void:
    if node.is_queued_for_deletion():
        return
    var script: Script = node.get_script() as Script
    var item: Dictionary = {"path": str(origin.get_path_to(node)), "name": str(node.name),
        "class": node.get_class(), "script": script.resource_path if script != null else "",
        "scene": node.scene_file_path}
    if node is Node3D:
        var n := node as Node3D
        item.merge({"local": _matrix(n.transform), "world": _matrix(n.global_transform),
            "visible": n.visible, "visible_in_tree": n.is_visible_in_tree()})
    if node is MeshInstance3D:
        item["mesh"] = _mesh(node as MeshInstance3D)
    if node is CollisionShape3D:
        item["collision"] = _shape(node as CollisionShape3D)
    if node is CollisionObject3D:
        var body := node as CollisionObject3D
        item["collision_layer"] = body.collision_layer
        item["collision_mask"] = body.collision_mask
    if node is Camera3D:
        var cam := node as Camera3D
        item["camera"] = {"fov_degrees": cam.fov, "near_m": cam.near, "far_m": cam.far,
            "projection": cam.projection, "current": cam.current,
            "keep_aspect": cam.keep_aspect}
    if node is Light3D:
        var light := node as Light3D
        item["light"] = {"color": _color(light.light_color), "energy": light.light_energy,
            "shadow": light.shadow_enabled}
    if node is WorldEnvironment:
        var env: Environment = (node as WorldEnvironment).environment
        if env != null:
            item["environment"] = {"background_mode": env.background_mode,
                "ambient_energy": env.ambient_light_energy, "fog_enabled": env.fog_enabled,
                "sky_material": env.sky.sky_material.get_class() if env.sky != null and env.sky.sky_material != null else null}
    if node is Label3D:
        item["text"] = (node as Label3D).text
    if node is Skeleton3D:
        var rig := node as Skeleton3D
        var bones: Array[Dictionary] = []
        for i in range(rig.get_bone_count()):
            bones.append({"name": rig.get_bone_name(i), "parent": rig.get_bone_parent(i),
                "rest": _matrix(rig.get_bone_rest(i)), "pose": _matrix(rig.get_bone_pose(i))})
        item["bones"] = bones
    if node is AnimationPlayer:
        item["animations"] = Array((node as AnimationPlayer).get_animation_list())
    if node is CanvasItem:
        var canvas := node as CanvasItem
        if canvas.material != null:
            item["canvas_material"] = _material(canvas.material)
    # Every node, including nonvisual ancestors, is retained to preserve hierarchy.
    rows.append(item)
    for child in node.get_children():
        _walk(child, origin, rows)

func _snapshot(label: String, node: Node, families: Array[String], context: Dictionary = {}) -> Dictionary:
    var rows: Array[Dictionary] = []
    _walk(node, node, rows)
    var counts: Dictionary = {"nodes": rows.size(), "mesh_nodes": 0, "colliders": 0, "skeletons": 0}
    for row in rows:
        if row.has("mesh") and not row["mesh"].get("missing", false):
            counts["mesh_nodes"] += 1
        if row.has("collision") and not row["collision"].get("missing", false):
            counts["colliders"] += 1
        if row.has("bones"):
            counts["skeletons"] += 1
    var sample: Dictionary = {"id": label, "families": families, "context": context,
        "counts": counts, "nodes": rows}
    samples.append(sample)
    return sample

func _screenshot(label: String) -> void:
    if DisplayServer.get_name() == "headless":
        return
    await process_frame
    await RenderingServer.frame_post_draw
    var image: Image = root.get_texture().get_image()
    _expect(not image.is_empty(), "empty screenshot " + label)
    if not image.is_empty():
        _expect(image.save_png(output_dir.path_join(label + ".png")) == OK, "save screenshot " + label)

func _pose(p: Variant, id: String, optic: String, muzzle: String, pose: String) -> void:
    p.equip(id)
    p.weapon_attachments[id] = {"optic": optic, "muzzle": muzzle}
    p._update_gun_mesh()
    p.equip_anim_timer = 0.0
    p.holster_timer = 0.0
    p.shot_anim = 0.0
    p.bolt_cycle_remaining = 0.0
    p.sprint_blend = 0.0
    p.weapon_wall_blend = 0.0
    p.idle_clock = 0.0
    p.walk_anim_blend = 0.0
    p.aim = pose == "ads"
    p.reloading = pose == "reload"
    p.reload_elapsed = float(SurvivalPlayer.WEAPONS[id]["reload"]) * 0.45 if p.reloading else 0.0
    p.camera.fov = p.get_target_camera_fov(false)
    p._update_viewmodel_projection(1.0, false, 22.0)
    p.gun.position = p.get_viewmodel_rest_pose(p.aim)
    p.gun.rotation = Vector3.ZERO
    p._animate_viewmodel(0.25, 0.0)
    if is_instance_valid(p.optic_reticle):
        p.optic_reticle.visible = p.aim
    var sample := _snapshot("fps_" + id + "_" + optic + "_" + muzzle + "_" + pose, p,
        ["viewmodel:assembly", "viewmodel:hands", "viewmodel:attachments", "player:collision",
        "effect:muzzle", "effect:scope_overlay", "material:weapon_overrides", "geometry:model_surface"],
        {"weapon": id, "optic": optic, "muzzle": muzzle, "pose": pose, "viewmodel_fov": p.viewmodel_fov})
    _expect(p.weapon_id == id and is_instance_valid(p.weapon_model) and is_instance_valid(p.hand_rig),
        "missing weapon/hand rig " + id)
    _expect(int(sample["counts"]["mesh_nodes"]) > 0 and int(sample["counts"]["colliders"]) > 0, "empty player " + id)
    if optic != "":
        _expect(p.viewmodel_root.find_child("Attachment_Optic_" + optic, true, false) != null, "missing optic " + id + " " + optic)
    if muzzle != "":
        _expect(p.viewmodel_root.find_child("Attachment_Muzzle_" + muzzle, true, false) != null, "missing muzzle " + id + " " + muzzle)

func _run() -> void:
    output_dir = OS.get_environment("FRONTLINE_INVENTORY_DIR")
    if output_dir.is_empty():
        push_error("ASSET_RUNTIME_ERROR: set FRONTLINE_INVENTORY_DIR to an isolated QA output directory")
        quit(1)
        return
    _expect(DirAccess.make_dir_recursive_absolute(output_dir) == OK, "output directory")
    var game: Variant = (load("res://scenes/main.tscn") as PackedScene).instantiate()
    game.checkpoint_path = "user://qa-inventory-" + str(OS.get_process_id()) + ".save"
    root.add_child(game)
    game.set_process(false)
    game.set_physics_process(false)
    var p: Variant = game.player
    p.set_physics_process(false)
    p.controls_locked = true
    var map_sample := _snapshot("map_briefing", game, ["map:campo_de_testes", "environment:lighting", "camera:briefing"],
        {"scene": "res://scenes/main.tscn", "shops": game.shops.size()})
    _expect(game.shops.size() == 3 and int(map_sample["counts"]["mesh_nodes"]) > 30 and int(map_sample["counts"]["colliders"]) > 4, "map composition incomplete")
    await _screenshot("map_briefing")
    game.game_menu._start()
    game.combat_hud_root.hide()
    p.camera.rotation = Vector3.ZERO
    seed(9133)
    for id in IDS:
        for pose in ["hip", "ads", "reload"]:
            _pose(p, id, "", "", pose)
        var optics: Array[String] = ["scope_2x", "scope_4x"] if id in ["sniper", "bolt_sniper"] else ["red_dot", "holo"]
        if id == "sentinela":
            optics.append("scope4")
        for optic in optics:
            _pose(p, id, optic, "", "ads")
        for muzzle in ["suppressor", "compensator"]:
            _pose(p, id, "", muzzle, "hip")
    _pose(p, "rifle", "red_dot", "", "ads")
    samples.pop_back() # pose repeated only for rendered evidence
    await _screenshot("fps_rifle_ads")
    _pose(p, "rifle", "", "", "hip")
    samples.pop_back() # pose repeated only for the NPC scene
    for kind in ["soldier", "runner", "heavy"]:
        for loadout in (["shotgun", "smg", "rifle", "lmg"] if kind != "heavy" else ["lmg"]):
            var enemy := SurvivalEnemy.new()
            enemy.configure(kind, 16, p, loadout)
            enemy.position = Vector3(0, 0.9, -6)
            game.add_child(enemy)
            enemy.set_physics_process(false)
            var e := _snapshot("enemy_" + kind + "_" + loadout, enemy, ["enemy:legacy"],
                {"kind": kind, "weapon": enemy.weapon_class})
            _expect(int(e["counts"]["mesh_nodes"]) > 0 and int(e["counts"]["colliders"]) > 0, "enemy missing " + kind)
            if kind == "soldier" and loadout == "rifle":
                await _screenshot("enemy_rifle")
            enemy.free()
    var experimental := SurvivalEnemy.new()
    experimental.configure("soldier", 16, p, "rifle")
    experimental.preview_quaternius = true
    experimental.position = Vector3(0, 0.9, -6)
    game.add_child(experimental)
    experimental.set_physics_process(false)
    var exp := _snapshot("enemy_quaternius_experimental", experimental, ["character:quaternius_equipment"],
        {"experimental": true, "active_in_default_game": false})
    _expect(int(exp["counts"]["skeletons"]) > 0 and is_instance_valid(experimental.humanoid_visual), "experimental rig fallback")
    await _screenshot("enemy_experimental")
    experimental.free()
    var ally := SurvivalAlly.new()
    ally.configure(p)
    ally.position = Vector3(2, 0.9, -6)
    game.add_child(ally)
    ally.set_physics_process(false)
    _snapshot("ally", ally, ["ally:legacy"])
    var turret := SurvivalTurret.new()
    turret.position = Vector3(-2, 0, -6)
    game.add_child(turret)
    turret.set_physics_process(false)
    _snapshot("turret", turret, ["object:turret"])
    for id in IDS:
        var pickup := Loot.new()
        pickup.configure("weapon", id)
        game.add_child(pickup)
        _snapshot("loot_weapon_" + id, pickup, ["object:loot"], {"weapon": id})
        pickup.free()
    var ammo := Loot.new()
    ammo.configure("ammo", "rifle")
    game.add_child(ammo)
    _snapshot("loot_ammo", ammo, ["object:loot"])
    ammo.free()
    var grenade := Grenade.new()
    grenade.configure(p, 1)
    grenade.position = Vector3(5, 1, -8)
    game.add_child(grenade)
    grenade.freeze = true
    _snapshot("grenade", grenade, ["object:grenade"])
    grenade._spawn_explosion_effects()
    _snapshot("grenade_effect", grenade, ["effect:grenade"])
    var blood := Blood.new()
    game.add_child(blood)
    _snapshot("blood_effect", blood, ["effect:blood"])
    # Invoke the existing visual event only; no real shooting or gameplay changes.
    p.equip("shotgun")
    game._on_shot_fired(p.camera.to_global(Vector3(0, 0, -5)), false)
    _snapshot("combat_visual_event", game, ["effect:combat"], {"sample": "shot visual callback"})
    var report: Dictionary = {"schema_version": 1, "kind": "frontline_runtime_inventory",
        "commit": OS.get_environment("GITHUB_SHA"), "godot": Engine.get_version_info(),
        "display": DisplayServer.get_name(), "coordinate_unit": "m",
        "samples": samples, "failures": failures,
        "limitations": ["finite sampled states, not exhaustive live instances", "no geometry buffers exported",
            "no explicit LOD index arrays", "physics queries are source-only", "airstrike and enemy tracer not sampled",
            "screenshots are not visual approval", "no Asset Studio yet"]}
    var file := FileAccess.open(output_dir.path_join("runtime_inventory.json"), FileAccess.WRITE)
    if file == null:
        _expect(false, "write inventory")
    else:
        file.store_string(JSON.stringify(report, "\t"))
        file.close()
    print("ASSET_RUNTIME_INVENTORY_PASS" if failures.is_empty() else "ASSET_RUNTIME_INVENTORY_FAIL")
    print("Samples: ", samples.size())
    quit(0 if failures.is_empty() else 1)
