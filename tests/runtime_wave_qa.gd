extends SceneTree
## CI integration test. Exercises actual Godot scene, enemies and transition
## through two waves, not just a parser/import smoke test.
const SpawnSelector = preload("res://scripts/spawn_selector.gd")
var failures: Array[String] = []
var checked: int = 0

func _initialize() -> void:
    call_deferred("_run_tests")

func _expect(condition: bool, message: String) -> void:
    checked += 1
    if not condition:
        failures.append(message)
        push_error("QA ERROR: " + message)

func _run_tests() -> void:
    var packed: PackedScene = load("res://scenes/main.tscn")
    _expect(packed != null, "main scene loads")
    if packed == null:
        quit(1)
        return
    var game: Variant = packed.instantiate()
    root.add_child(game)
    await physics_frame
    # The menu deliberately pauses the game until the player starts.
    game.game_menu._start()
    await physics_frame
    _expect(game.phase == "break", "initial phase is preparation")
    _expect(game.wave == 0, "initial wave not yet started")
    _expect(game.player != null, "player was instantiated")
    _expect(game.shops.size() == 3, "physical shops preserved")
    # HUD v0.9.19: NO five large dark cards; only type, hairlines and a
    # contextual 30px prompt. Geometry anchors adapt to aspect ratio.
    _expect(game.hud_groups.size() >= 9, "edge-anchored combat HUD zones are missing")
    _expect(game.combat_hud_root != null and game.combat_hud_root.name == "CombatHUD",
        "combat HUD root missing")
    _expect((game.hud_groups["Credits"] as Control).anchor_left == 0.0
        and (game.hud_groups["Wave"] as Control).anchor_left == 0.5
        and (game.hud_groups["Support"] as Control).anchor_left == 1.0,
        "top instruments are not correctly anchored to the viewport")
    _expect((game.hud_groups["Vitals"] as Control).anchor_top == 1.0
        and (game.hud_groups["Weapon"] as Control).anchor_top == 1.0
        and (game.hud_groups["Weapon"] as Control).anchor_left == 1.0,
        "vitals/ammo must track screen corners on resize")
    _expect(game.interaction_panel.size.y <= 32.0 and game.interaction_panel.size.x <= 335.0,
        "interaction tooltip is too large")
    _expect(game.report_background.get_theme_stylebox("panel") is StyleBoxEmpty
        and game.banner_panel.get_theme_stylebox("panel") is StyleBoxEmpty,
        "wave notifications must not draw generic modal backgrounds")
    _expect(game.hitmarker.anchor_left == 0.5 and game.hitmarker.anchor_top == 0.5,
        "hitmarker must stay at the real viewport center")
    _expect(game.wave_progress.size.x < 390.0 and game.wave_progress.scale.y < 0.5,
        "wave progress should be thin and small")
    var big_card_count := 0
    var minimal_strokes := 0
    for zone in game.hud_groups.values():
        for child in (zone as Control).get_children():
            if child is Polygon2D:
                big_card_count += 1
            if child is Line2D:
                minimal_strokes += 1
    _expect(big_card_count == 0 and minimal_strokes >= 5,
        "combat instruments must be text/hairlines instead of opaque polygons")
    game.banner_timer = 1.0
    game.report_remaining = 1.0
    game.status_timer = 1.0
    game._refresh_ui()
    _expect(game.banner_panel.visible and not game.report_background.visible
        and not game.message_hud.visible,
        "two or three event notifications are overlapping each other")
    game.banner_timer = 0.0
    game._refresh_ui()
    _expect(game.report_background.visible and not game.message_hud.visible,
        "wave recap should have priority over status warnings")
    game.report_remaining = 0.0
    game.status_timer = 0.0
    game._refresh_ui()
    # The four actual settings categories must be reachable from the pause UI.
    var menu: Variant = game.game_menu
    _expect(menu != null and not menu.active, "game starts/resumes outside menu")
    menu.open_pause()
    _expect(menu.active and paused, "pause menu must stop gameplay")
    menu._show_options()
    _expect(menu.in_options and menu.settings_tabs.visible, "settings tabs are hidden")
    for category in ["graphics", "audio", "controls", "gameplay"]:
        menu._select_category(category)
        _expect(menu.settings_category == category and menu.options.get_child_count() > 1,
            "missing options page: " + category)
    menu._back_options()
    _expect(not menu.in_options, "settings back button failed")
    menu.resume()
    _expect(not paused and not menu.active, "resuming the game from pause failed")
    var settings_node: Node = root.get_node_or_null("GameSettings")
    _expect(settings_node != null and int(settings_node.get("intermission_seconds")) >= 30,
        "30-second intervals are unavailable")
    if settings_node != null:
        var old_scale: float = float(settings_node.get("render_scale"))
        settings_node.call("set_value", "render_scale", 0.8)
        _expect(absf(float(root.scaling_3d_scale) - 0.8) < 0.01,
            "Graphics render scale does not change the real 3D viewport")
        settings_node.call("set_value", "render_scale", old_scale)
        var old_inverted: bool = bool(settings_node.get("invert_mouse_y"))
        settings_node.call("set_value", "invert_y", not old_inverted)
        _expect(bool(settings_node.get("invert_mouse_y")) != old_inverted,
            "inverted mouse control not applied")
        settings_node.call("set_value", "invert_y", old_inverted)
        var hitmarker_old: bool = bool(settings_node.get("hitmarker_enabled"))
        settings_node.call("set_value", "hitmarker", false)
        game.hitmarker.visible = false
        game._on_hit_confirmed()
        _expect(not game.hitmarker.visible, "disabled hitmarker should not flash")
        settings_node.call("set_value", "hitmarker", hitmarker_old)
    # Pages exist because each physical store has more than five options.
    game.wallet = 6000
    game._open_shop("weapons")
    _expect(game.shop_option_buttons[4].visible, "red-dot option missing from weapons store")
    game._buy(4) # red dot on initial pistol, no attachment by default
    _expect(game.player.has_attachment("optic", "red_dot"), "red dot failed to install")
    _expect(game.player.viewmodel_root.find_child("Attachment_Optic_red_dot", true, false) != null,
        "paid red dot has no visible 3D model")
    var scope: Node3D = game.player.viewmodel_root.find_child("Attachment_Optic_red_dot", true, false)
    _expect(scope.find_child("Optic_HollowRing", true, false) != null,
        "Red Dot lacks a hollow, see-through physical sight")
    _expect(scope.find_child("Optic_TransparentLens", true, false) != null,
        "Red Dot lacks a transparent lens")
    _expect(scope.find_child("Optic_RailMount", true, false) != null,
        "Red Dot has no rail attachment")
    var reticle: MeshInstance3D = scope.find_child("Optic_EmissiveReticle", true, false) as MeshInstance3D
    _expect(reticle != null and not reticle.visible,
        "Red Dot emitter must not draw while hip-firing")
    if reticle != null:
        _expect(absf(reticle.position.x) < 0.001 and reticle.mesh is SphereMesh,
            "Red Dot must have a centered physical emitter, not a floating HUD crosshair")
    game._change_shop_page(1)
    _expect(game.shop_page == 1, "shop pagination failed")
    game._buy(1) # suppressor
    _expect(game.player.has_attachment("muzzle", "suppressor"),
        "suppressor failed to install alongside red dot")
    _expect(game.player.viewmodel_root.find_child("Attachment_Muzzle_suppressor", true, false) != null,
        "paid suppressor has no visible barrel attachment")
    _expect(game.player.shot_sound.bus == "SUPPRESSED",
        "silencer must use the recorded WAV through low-pass audio, not a beep")
    var wallet_after_suppressor: int = game.wallet
    game._buy(1)
    _expect(game.wallet == wallet_after_suppressor, "already-equipped suppressor charged twice")
    game._close_shop()
    game.player.equip("smg")
    _expect(not game.player.has_attachment("optic", "red_dot"),
        "red dot must be bought per weapon, not copied between guns")
    game.player.equip("pistol")
    _expect(game.player.has_attachment("optic", "red_dot"),
        "changing weapons lost paid pistol optic")
    game._open_shop("support")
    game._buy(3) # quick reload perk
    _expect(game.player.active_perk == "quick_reload", "perk purchase did not apply")
    game._buy(4) # steady replaces quick reload
    _expect(game.player.active_perk == "steady", "perks must replace, never stack")
    game._close_shop()
    game._open_shop("gear")
    game._change_shop_page(1)
    game._buy(0) # revival kit
    _expect(game.player.self_revive_kits == 1, "self revive kit not delivered")
    var wallet_after_kit: int = game.wallet
    game._buy(0)
    _expect(game.wallet == wallet_after_kit, "duplicate revive kit charged twice")
    game._close_shop()
    # Posture is physical, not merely walking speed.
    game.player._update_posture(0.5, true)
    _expect(game.player.capsule_shape.height < 1.3, "crouch did not shrink collider")
    game.player.prone_requested = true
    game.player._update_posture(0.5, false)
    _expect(game.player.capsule_shape.height < 0.85, "prone did not lower collision capsule")
    _expect(game.player.posture == "prone", "Z posture state missing")
    game.player.prone_requested = false
    game.player._update_posture(0.5, false)
    _expect(game.player.capsule_shape.height > 1.3, "standing from prone failed in open space")
    # Exercise real 60 FPS transition frames; a one-call snap misses camera
    # clipping that happens while the capsule is changing its height.
    game.player.set_physics_process(false)
    game.player.prone_requested = true
    for step in range(22):
        game.player._update_posture(1.0 / 60.0, false)
        var top: float = game.player.collider_node.position.y + game.player.capsule_shape.height * 0.5
        var bottom: float = game.player.collider_node.position.y - game.player.capsule_shape.height * 0.5
        _expect(game.player.camera.position.y <= top - 0.115,
            "camera escaped collider while lowering at frame %d" % step)
        _expect(absf(bottom + 0.9) < 0.015,
            "capsule feet drifted while lowering at frame %d" % step)
    game.player.prone_requested = false
    for frame_up in range(22):
        game.player._update_posture(1.0 / 60.0, false)
        var top_standing: float = game.player.collider_node.position.y + game.player.capsule_shape.height * 0.5
        _expect(game.player.camera.position.y <= top_standing - 0.115,
            "camera escaped collider while standing at frame %d" % frame_up)
    game.player._update_posture(0.5, false)
    _expect(game.player.posture == "stand" and game.player.current_body_height > 1.79,
        "posture transition did not finish standing up in an open area")
    # A physical ceiling permits crouch/prone but must reject a stand-up.
    game.player._update_posture(0.5, true)
    var test_roof := StaticBody3D.new()
    test_roof.collision_layer = 1
    test_roof.collision_mask = 0
    var test_roof_collider := CollisionShape3D.new()
    var test_roof_box := BoxShape3D.new()
    test_roof_box.size = Vector3(3.0, 0.2, 3.0)
    test_roof_collider.shape = test_roof_box
    test_roof.add_child(test_roof_collider)
    game.add_child(test_roof)
    # The player's capsule bottom is always 0.9 m below its origin.
    # The ceiling begins 1.4 m above the feet, above crouch but below stand.
    test_roof.global_position = game.player.global_position + Vector3.UP * 0.6
    await physics_frame
    _expect(not game.player._can_expand_to_height(1.8),
        "physics roof should block expanding the capsule to standing height")
    game.player._update_posture(0.5, false)
    _expect(game.player.posture == "crouch" and game.player.current_body_height <= 1.18,
        "releasing crouch under a physical roof must not force standing")
    var capsule_bottom: float = game.player.collider_node.position.y - game.player.capsule_shape.height * 0.5
    _expect(absf(capsule_bottom + 0.9) < 0.015,
        "crouch should keep the capsule feet at the same vertical position")
    game.player.prone_requested = true
    game.player._update_posture(0.5, false)
    _expect(game.player.posture == "prone" and game.player.current_body_height < 0.85,
        "prone must fit below the low ceiling")
    var capsule_top: float = game.player.collider_node.position.y + game.player.capsule_shape.height * 0.5
    _expect(game.player.camera.position.y <= capsule_top - 0.115,
        "camera must stay below the prone capsule top instead of clipping the ceiling")
    game.player.prone_requested = false
    game.player._update_posture(0.5, false)
    _expect(game.player.posture == "prone",
        "letting go of prone under a roof must wait for stand-up clearance")
    game.player._update_posture(0.5, true)
    _expect(game.player.posture == "crouch" and game.player.capsule_shape.height < 1.3,
        "low ceiling must still allow a safe prone-to-crouch transition")
    game.player.downed = true
    game.player._update_posture(0.5, false)
    _expect(game.player.posture == "downed", "Last Stand should use the low physical capsule")
    game.player.downed = false
    game.player._update_posture(0.5, false)
    _expect(game.player.posture == "prone",
        "Last Stand recovery under a roof must not keep a stale downed posture")
    test_roof.queue_free()
    await physics_frame
    game.player._update_posture(0.5, false)
    _expect(game.player.posture == "stand" and game.player.capsule_shape.height > 1.79,
        "player must stand again once the physical roof is removed")
    game.player.set_physics_process(true)
    # A real lethal hit first gives a ten-second pistol last stand.
    game.player.invulnerability_timer = 0.0
    game.player.health = 8.0
    game.player.take_damage(200.0, game.player.global_position + Vector3.BACK)
    _expect(game.player.downed and not game.player.dead, "last stand skipped downed state")
    _expect(game.player.weapon_id == "pistol" and game.player.downed_seconds > 0.0,
        "last stand must provide pistol and a countdown")
    game.player.downed_seconds = 0.01
    game.player._physics_process(0.1)
    _expect(not game.player.downed and not game.player.dead,
        "pre-purchased revival kit did not recover from last stand")
    _expect(game.player.self_revive_kits == 0 and game.player.health >= 35.0,
        "revival kit was not consumed correctly")
    game.player.invulnerability_timer = 10.0
    # Test a real payout from the Game controller, not just pure RoundStats.
    game.phase = "wave"
    game.round_stats.begin(1)
    var before_challenge: int = game.wallet
    for k in range(4):
        game._on_shot_resolved(true, false)
        game._on_enemy_combat_defeat(9000 + k, "player", false, k + 1, 50)
    _expect(game.wallet == before_challenge + 500,
        "game economy did not pay rapid-kill challenge once")
    _expect(game.round_stats.shots == 4 and game.round_stats.hits == 4,
        "game failed one-shot-one-trigger tracking")
    # The second downed encounter may recover through a player kill but a
    # support-soldier kill must not improperly give the player a second chance.
    game.player.last_stand_available = true
    game.player.invulnerability_timer = 0.0
    game.player.health = 3.0
    game.player.take_damage(100.0)
    _expect(game.player.downed and game.player.magazines["pistol"] >= 8,
        "second last stand or emergency pistol ammunition failed")
    game.phase = "wave"
    game.round_stats.begin(1)
    game._on_enemy_combat_defeat(9555, "support", false, 0, 50)
    _expect(game.player.downed, "an allied soldier erroneously revived downed player")
    game._on_enemy_combat_defeat(9556, "player", false, 1, 50)
    _expect(not game.player.downed and game.player.health >= 35.0,
        "a player pistol kill did not recover last stand")
    game.phase = "break"
    # Combat contract: cancelled reloads must never create ammunition.
    game.player.sprint_blend = 0.0
    game.player.melee_timer = 0.0
    game.player.grenade_throw_timer = 0.0
    game.player.equip("rifle")
    game.player.magazines["rifle"] = 3
    game.player.reserves["rifle"] = 12
    game.player.start_reload()
    _expect(game.player.reloading and game.player.reload_timer > 0.0,
        "manual reload with available reserve did not start")
    game.player.switch_weapon("pistol", true)
    _expect(not game.player.reloading and game.player.magazines["rifle"] == 3
        and game.player.reserves["rifle"] == 12,
        "switching weapons must cancel reload without creating ammunition")
    game.player.switch_weapon("rifle", true)
    game.player._finish_reload()
    _expect(game.player.magazines["rifle"] == 3 and game.player.reserves["rifle"] == 12,
        "a cancelled reload callback must not transfer ammunition")
    game.player.start_reload()
    game.player._finish_reload()
    _expect(game.player.magazines["rifle"] == 15 and game.player.reserves["rifle"] == 0
        and not game.player.reloading,
        "partial reload must consume only remaining reserve ammunition")
    game.player.magazines["rifle"] = 10
    game.player.reserves["rifle"] = 20
    game.player.controls_locked = true
    game.player.start_reload()
    _expect(not game.player.reloading, "shop/menu input lock must block starting a reload")
    game.player.controls_locked = false
    game.player.melee_timer = 0.5
    game.player.start_reload()
    _expect(not game.player.reloading, "reloading during a melee attack must be blocked")
    game.player.fire_timer = 0.0
    game.player.equip_anim_timer = 0.0
    game.player.shoot()
    _expect(game.player.magazines["rifle"] == 10,
        "shooting during a melee attack must not spend ammunition")
    game.player.melee_timer = 0.0
    game.player.equip_anim_timer = 0.3
    game.player.shoot()
    _expect(game.player.magazines["rifle"] == 10,
        "shooting before equip animation ends must be blocked")
    game.player.equip_anim_timer = 0.0
    game.player.fire_timer = 0.72
    game.player.switch_weapon("pistol", true)
    _expect(game.player.fire_timer >= 0.72,
        "weapon swap must not bypass previous shotgun-rate cooldown")
    game.player.switch_weapon("rifle", true)
    _expect(game.player.fire_timer >= 0.72,
        "switching back immediately must not reset the firing cooldown")
    game.player.switch_weapon("pistol", true)
    game.player.downed = true
    game.player.switch_weapon("rifle", true)
    _expect(game.player.weapon_id == "pistol",
        "last stand must reject a non-pistol weapon even on forced swap")
    game.player.downed = false
    game.player.fire_timer = 0.0
    game.player.equip_anim_timer = 0.0
    game.player.equip("smg")
    game.player.equip("rifle")
    game.player.switch_weapon("smg", true)
    _expect(game.player.last_primary == "smg",
        "switching to an owned primary must update the quick-toggle primary")
    game.player.switch_weapon("pistol", true)
    _expect(game.player.last_primary == "smg",
        "pistol swap must remember the last actually equipped primary")
    game.player.downed = true
    game.player.equip("rifle")
    _expect(game.player.weapon_id == "pistol" and game.player.last_primary == "smg",
        "downed pickup must not overwrite the remembered active primary")
    game.player.downed = false
    # Tactical sprint suppresses fire, distinct from merely speeding up walking.
    var original_ammo: int = int(game.player.magazines[game.player.weapon_id])
    game.player.sprint_blend = 1.0
    game.player.shoot()
    _expect(game.player.magazines[game.player.weapon_id] == original_ammo,
        "sprinting should keep the gun lowered rather than firing")
    _expect(game.player.grenade_throw_timer == 0.0, "grenade throw should be ready before action")
    game.player.sprint_blend = 1.0
    game.player.walk_clock = 2.1
    game.player.sprint_stride = -0.55
    game.player._animate_viewmodel(0.18, 1.0)
    _expect(game.player.left_hand_rig.position.y < -0.18,
        "sprint support arm should drop separately from walking")
    game.player.sprint_blend = 0.0
    game.player.sprint_stride = 0.0
    game.player._animate_viewmodel(0.18, 0.0)
    # G must launch a REAL rigid body with fuse, gravity, bounce and blast.
    var grenades_before: int = game.grenades
    game._throw_grenade()
    await physics_frame
    _expect(game.grenades == grenades_before - 1,
        "G must consume precisely one frag grenade")
    _expect(game.player.grenade_throw_timer > 0.0,
        "throw animation did not play")
    var projectiles := get_nodes_in_group("live_grenades")
    _expect(projectiles.size() == 1,
        "grenade must spawn as a physical RigidBody3D, not instant area damage")
    if not projectiles.is_empty():
        var frag: Variant = projectiles[0]
        _expect(frag is RigidBody3D and frag.linear_velocity.length() > 10.0,
            "grenade launch must have ballistic velocity")
        _expect(frag.fuse_remaining > 1.0 and not frag.exploded,
            "grenade exploded at the moment G was pressed")
        _expect(frag.physics_material_override.bounce > 0.25,
            "grenade should ricochet off hard geometry")
        _expect(frag.explosion_sound.stream != null,
            "recorded CC0 explosion asset was not packaged")
        frag._detonate()
        _expect(frag.exploded and frag.get_node_or_null("ShockwaveRing") != null,
            "detonation did not create shockwave and visual blast")
        _expect(frag.get_node_or_null("BlastLight") != null,
            "grenade blast should briefly illuminate the area")
        frag.queue_free()
    game.player.grenade_throw_timer = 0.0
    # Hitmarker must not be an always-on crosshair, and requires no audio.
    _expect(not game.hitmarker.visible, "hitmarker is displayed permanently")
    game._on_hit_confirmed()
    _expect(game.hitmarker.visible, "confirmed enemy hit is not visible")
    game._on_headshot()
    _expect(game.hitmarker.get("headshot"), "headshot tint not set")
    # Tactical NPCs now have finite magazines, reload, cover states, and
    # physical crouch/prone profiles rather than a nonstop rush-and-fire loop.
    var tactics_script: Variant = load("res://scripts/enemy_tactics.gd")
    _expect(tactics_script.magazine_size("rifle") == 30,
        "enemy rifle magazine capacity incorrect")
    _expect(tactics_script.reload_duration("lmg") >= 3.0,
        "LMG should have a noticeably longer reload")
    var tactical_script: Script = load("res://scripts/enemy.gd")
    var tactical_npc: Variant = tactical_script.new()
    tactical_npc.configure("soldier", 7, game.player, "rifle")
    tactical_npc.position = Vector3(-6.0, 1.5, -6.0)
    game.add_child(tactical_npc)
    _expect(tactical_npc.ammo_in_mag == 30,
        "NPC must start with a finite rifle magazine")
    _expect(tactical_npc.weapon_pivot.position.y > 0.27,
        "enemy rifle is still mounted in the abdomen rather than at the shoulder")
    tactical_npc.ammo_in_mag = 0
    tactical_npc._start_reload()
    _expect(tactical_npc.reload_remaining > 1.5,
        "NPC did not begin a real reload")
    _expect(tactical_npc.reload_audio != null and tactical_npc.reload_audio.stream != null,
        "NPC reload must use existing recorded WAV")
    tactical_npc.reload_remaining = 0.01
    tactical_npc.attack_cooldown = 100.0
    tactical_npc._physics_process(0.05)
    _expect(tactical_npc.ammo_in_mag == 30,
        "NPC reload did not refill the magazine")
    tactical_npc._set_tactical_posture("crouch")
    _expect(tactical_npc.tactical_posture == "crouch" and tactical_npc.hit_collider.shape.height < 1.4,
        "NPC crouch should shrink the real collider")
    tactical_npc._set_tactical_posture("prone")
    _expect(tactical_npc.tactical_posture == "prone" and tactical_npc.hit_collider.shape.height < 0.9,
        "NPC prone should shrink the real collider")
    tactical_npc._set_tactical_posture("stand")
    _expect(tactical_npc.hit_collider.shape.height >= 1.75,
        "NPC must stand after crouch/prone")
    var cover_candidate: Dictionary = {}
    for site in [Vector3(-6.0, 1.5, -5.0), Vector3(-12.0, 1.5, -6.0),
                 Vector3(8.0, 1.5, 5.0), Vector3(12.0, 1.5, 8.0)]:
        tactical_npc.global_position = site
        cover_candidate = tactics_script.find_cover(tactical_npc, game.player.global_position)
        if not cover_candidate.is_empty():
            break
    _expect(not cover_candidate.is_empty(), "Camp of Tests has no reachable cover positions")
    if not cover_candidate.is_empty():
        _expect(tactics_script._hidden_from_player(
            game.get_world_3d().direct_space_state,
            cover_candidate["position"], game.player.global_position
        ), "cover position must block player line of sight")
    tactical_npc.queue_free()
    # A dropped gun and an ammunition box must be collectible with no UI shop.
    game._spawn_loot_pickup("weapon", "smg", game.player.global_position, 0)
    var weapon_drop: Node3D = game._nearest_loot()
    _expect(weapon_drop != null, "weapon pickup not found near player")
    if weapon_drop != null:
        game._collect_loot(weapon_drop)
        _expect(game.player.owned_weapons.has("smg"), "ground weapon not added to inventory")
    game.player.reserves["smg"] = 0
    # A drop's caliber must match its originating weapon, not the held weapon.
    game._spawn_loot_pickup("ammo", "smg", game.player.global_position, 16)
    var ammunition: Node3D = game._nearest_loot()
    _expect(ammunition != null, "ammunition drop not found")
    if ammunition != null:
        game._collect_loot(ammunition)
        _expect(game.player.reserves["smg"] == 16, "same-weapon ammunition not credited")
    var previous_reserve: int = game.player.reserves["smg"]
    # Rifle was acquired in the weapon-swap QA above; LMG remains unowned here.
    _expect(not game.player.owned_weapons.has("lmg"),
        "unowned caliber QA requires the LMG to be unavailable at this point")
    game._spawn_loot_pickup("ammo", "lmg", game.player.global_position, 16)
    var unowned_ammo: Node3D = game._nearest_loot()
    _expect(unowned_ammo != null, "unowned-caliber ammo spawn missing")
    if unowned_ammo != null:
        game._collect_loot(unowned_ammo)
        _expect(game.player.reserves["smg"] == previous_reserve,
            "unowned LMG ammo incorrectly converted to equipped SMG ammo")
        _expect(not unowned_ammo.is_queued_for_deletion(),
            "unowned caliber should stay on the ground until picked up with its weapon")
        unowned_ammo.queue_free()
    # Test attachments and gun models on ALL five classes, not only the pistol.
    for gun_id in ["pistol", "smg", "rifle", "shotgun", "lmg"]:
        game.player.equip(gun_id)
        game.player.install_attachment("optic", "red_dot")
        game.player.install_attachment("muzzle", "suppressor")
        _expect(game.player.has_attachment("optic", "red_dot"),
            "Red Dot unavailable on " + gun_id)
        _expect(game.player.has_attachment("muzzle", "suppressor"),
            "Suppressor unavailable on " + gun_id)
        _expect(game.player.viewmodel_root.find_child("Attachment_Optic_red_dot", true, false) != null,
            "Red Dot has no model on " + gun_id)
        _expect(game.player.viewmodel_root.find_child("Attachment_Muzzle_suppressor", true, false) != null,
            "Suppressor has no model on " + gun_id)
    game.player.equip("pistol")
    # The unanimated Quaternius experiment is never activated in public waves.
    _expect(not game._is_humanoid_preview_enabled(),
        "Public gameplay must use stable enemy models until rig animations are approved")
    # Real death leaves a non-colliding corpse and a dropped weapon for pickup.
    # Dynamically load after the project scene initializes autoloads.
    # A hard SurvivalEnemy type dependency from SceneTree test startup can
    # compile player.gd before the GameSettings singleton is available.
    var fallen_script: Script = load("res://scripts/enemy.gd")
    var fallen: Variant = fallen_script.new()
    fallen.configure("soldier", 1, game.player, "rifle")
    fallen.preview_quaternius = true
    fallen.position = Vector3(11.0, 1.5, 11.0)
    fallen.loot_dropped.connect(game._on_enemy_loot_dropped)
    game.add_child(fallen)
    _expect(fallen.humanoid_visual != null, "Quaternius model did not replace selected soldier")
    if fallen.humanoid_visual != null:
        var preview: Node3D = fallen.humanoid_visual
        _expect(preview.get("valid"), "Quaternius imported character skeleton is invalid")
        var rig: Skeleton3D = preview.get("skeleton")
        _expect(rig != null and rig.get_bone_count() >= 50,
            "Quaternius model is missing its humanoid bone structure")
        if rig != null:
            for required_bone in ["Head", "spine_03", "upperarm_l", "upperarm_r", "thigh_l", "thigh_r"]:
                _expect(rig.find_bone(required_bone) >= 0,
                    "Quaternius model missing required bone " + required_bone)
            rig.force_update_all_bone_transforms()
            var head_y: float = rig.to_global(rig.get_bone_global_pose(rig.find_bone("Head")).origin).y
            var pelvis_y: float = rig.to_global(rig.get_bone_global_pose(rig.find_bone("pelvis")).origin).y
            var left_foot_y: float = rig.to_global(rig.get_bone_global_pose(rig.find_bone("foot_l")).origin).y
            var left_hand: Vector3 = rig.to_global(rig.get_bone_global_pose(rig.find_bone("hand_l")).origin)
            var right_hand: Vector3 = rig.to_global(rig.get_bone_global_pose(rig.find_bone("hand_r")).origin)
            var shoulder: Vector3 = rig.to_global(rig.get_bone_global_pose(rig.find_bone("upperarm_l")).origin)
            print("QUATERNIUS_GEOMETRY head_y=%.3f pelvis_y=%.3f foot_y=%.3f hands=%.3f,%.3f shoulder=%.3f" % [head_y, pelvis_y, left_foot_y, left_hand.y, right_hand.y, shoulder.y])
            _expect(head_y > pelvis_y + 0.25, "BUG: inverted Quaternius torso/head")
            _expect(pelvis_y > left_foot_y + 0.25, "BUG: inverted Quaternius legs")
            _expect(left_hand.y < head_y - 0.04 and right_hand.y < head_y - 0.04,
                "BUG: Quaternius arms raised above face like screenshot")
            var original_rotations: Dictionary = preview.get("base_bone_rotations")
            for controlled_bone in ["upperarm_l", "upperarm_r", "lowerarm_l", "lowerarm_r", "thigh_l", "thigh_r", "calf_l", "calf_r", "spine_03"]:
                var bone_idx: int = rig.find_bone(controlled_bone)
                var original_rotation: Quaternion = original_rotations.get(controlled_bone, Quaternion.IDENTITY)
                var offset: float = rig.get_bone_pose_rotation(bone_idx).angle_to(original_rotation)
                _expect(offset < 0.60, "BUG: excessive bone pose override: " + controlled_bone)
            _expect(head_y - left_foot_y > 0.90 and head_y - left_foot_y < 2.40, "BUG: distorted Quaternius body height")
        var legacy_torso := fallen.get_node_or_null("VisualRig/Spine/TacticalJacket") as MeshInstance3D
        _expect(legacy_torso != null and not legacy_torso.visible,
            "Original blocky enemy body must be hidden for Quaternius preview")
        _expect(is_instance_valid(fallen.weapon_pivot) and fallen.weapon_pivot.visible,
            "Existing weapon was hidden by humanoid replacement")
    await physics_frame
    fallen.take_damage(9999.0)
    _expect(fallen.dead and fallen.is_in_group("fallen_soldiers"), "enemy corpse not preserved")
    _expect(not fallen.is_queued_for_deletion(), "corpse despawned immediately")
    _expect(get_nodes_in_group("world_loot").size() >= 1, "enemy failed to drop a weapon")
    game._on_shot_fired(fallen.global_position, true)
    _expect(get_nodes_in_group("blood_fx").size() >= 1, "blood FX absent on a confirmed hit")
    fallen.queue_free()
    # Previous release had uncolored GLBs: inspect the actual imported scene
    # material on the pistol and make sure the vertex palette is enabled.
    var model_root: Node = game.player.weapon_model
    _expect(model_root != null, "first-person weapon model exists")
    if model_root != null:
        var pending: Array[Node] = [model_root]
        var found_palette := false
        while not pending.is_empty():
            var part: Node = pending.pop_back()
            if part is MeshInstance3D:
                var mi: MeshInstance3D = part as MeshInstance3D
                if mi.material_override is StandardMaterial3D:
                    var material: StandardMaterial3D = mi.material_override
                    found_palette = found_palette or material.vertex_color_use_as_albedo
            for child in part.get_children():
                pending.append(child)
        _expect(found_palette, "weapon GLB palette was not applied on runtime mesh")
    # Previous allied rigs were broken. Spawn and animate two support soldiers.
    game.ally_tokens = 1
    game._call_squad()
    _expect(get_nodes_in_group("allies").size() == 2, "squad did not deploy two allies")
    for frame in range(12):
        await physics_frame
    _expect(get_nodes_in_group("allies").size() == 2, "allies crashed during procedural animation")
    # Screenshot regression: the support soldier's head must be attached to
    # the torso by a collar and use the same pivot as the helmet/mask.
    for support in get_nodes_in_group("allies"):
        var head: Node3D = support.get_node_or_null("AllyVisual/HeadPivot")
        var neck: Node3D = support.get_node_or_null("AllyVisual/NeckCollar")
        _expect(head != null and neck != null, "support head or collar missing")
        if head != null:
            _expect(head.position.y <= 0.69, "support head disconnected from torso silhouette")
        _expect(is_instance_valid(support.muzzle), "support rifle or muzzle missing")
        _expect(support.gun_mount.position.y > 0.27,
            "allied support gun mount is still at belly height")
    var starting_weapon: String = game.player.weapon_id
    for weapon: String in ["pistol", "smg", "rifle", "shotgun", "lmg"]:
        game.player.weapon_id = weapon
        game.player._update_shot_audio()
        var shot: AudioStreamWAV = game.player.shot_sound.stream as AudioStreamWAV
        _expect(shot != null and shot.resource_path == "res://assets/audio/weapons/%s.wav" % weapon,
                "player shot does not use the expected recording: " + weapon)
        _expect(_matches_source_pcm(shot), "import changed shot PCM: " + weapon)
        var reload_clip := game.player.reload_sound.stream as AudioStreamWAV
        _expect(reload_clip != null and reload_clip.resource_path == "res://assets/audio/reloads/%s.wav" % weapon,
                "player reload does not use the expected recording: " + weapon)
        _expect(_matches_source_pcm(reload_clip), "import changed reload PCM: " + weapon)
    game.player.weapon_id = starting_weapon
    game.player._update_shot_audio()

    # FPS hand animation regression: the support hand reaches the magazine on
    # all three magazine-fed long guns and returns to the foregrip afterwards.
    var saved_primary: String = game.player.last_primary
    var saved_grenade_timer: float = game.player.grenade_throw_timer
    game.player.grenade_throw_timer = 0.0
    game.player.sprint_stride = 0.0
    # Resolve balance constants through the instantiated player script.
    # A direct SurvivalPlayer class reference can compile before the game's
    # GameSettings autoload has been registered in headless script tests.
    var reload_specs: Dictionary = game.player.get_script().get_script_constant_map().get("WEAPONS", {})
    _expect(reload_specs.has("smg") and reload_specs.has("shotgun"),
        "player weapon reload configuration missing in animation QA")
    var mag_sockets: Dictionary = game.player.get_script().get_script_constant_map().get("MAGAZINE_GRIP_POINTS", {})
    _expect(mag_sockets.size() == 3,
        "the three detachable magazine models must have their own grip socket")
    var reload_hand_travel: Dictionary = {}
    for gun_id: String in ["smg", "rifle", "lmg"]:
        game.player.equip(gun_id)
        game.player.reloading = true
        game.player.reload_elapsed = float(reload_specs[gun_id]["reload"]) * 0.45
        game.player._animate_viewmodel(0.20, 0.0)
        _expect(game.player.left_hand_rig.position.z > 0.22
            and game.player.left_hand_rig.position.y < -0.19,
            "support hand failed to reach magazine while reloading " + gun_id)
        reload_hand_travel[gun_id] = game.player.left_hand_rig.position.z
        var support_palm := game.player.left_hand_rig.get_node_or_null(
            "SupportShoulder/Elbow/Wrist/Palm") as Node3D
        _expect(support_palm != null and game.player.magazine_part != null,
            "magazine contact QA missing real support palm or moving mesh " + gun_id)
        if support_palm != null and game.player.magazine_part != null:
            var grip_local: Vector3 = mag_sockets[gun_id]
            var grip_position: Vector3 = game.player.magazine_part.transform * grip_local
            var palm_position: Vector3 = game.player.viewmodel_root.to_local(support_palm.global_position)
            _expect(grip_position.distance_to(palm_position) < 0.15,
                "support palm misses actual magazine contact on " + gun_id)
        game.player.reloading = false
        game.player.reload_elapsed = 0.0
        game.player._animate_viewmodel(0.20, 0.0)
        _expect(game.player.left_hand_rig.position.length() < 0.02,
            "support hand did not return to the foregrip after " + gun_id)
    _expect(reload_hand_travel["lmg"] > reload_hand_travel["rifle"] + 0.10,
        "LMG drum must require more hand travel than the rifle magazine")
    # Unlike box-magazine guns, the shotgun support hand follows its pump.
    game.player.equip("shotgun")
    game.player.reloading = true
    game.player.reload_elapsed = float(reload_specs["shotgun"]["reload"]) * 0.70
    game.player._animate_viewmodel(0.20, 0.0)
    var expected_pump: float = sin(0.70 * PI * 2.0) * 0.12
    _expect(absf(game.player.left_hand_rig.position.z - expected_pump) < 0.015,
        "shotgun support hand must track the pump during reload")
    var pump_socket: Vector3 = game.player.get_script().get_script_constant_map().get(
        "SHOTGUN_PUMP_GRIP_POINT", Vector3.ZERO)
    var pump_palm := game.player.left_hand_rig.get_node_or_null(
        "SupportShoulder/Elbow/Wrist/Palm") as Node3D
    _expect(pump_palm != null and game.player.action_part != null,
        "shotgun pump contact requires a rendered palm and action mesh")
    if pump_palm != null and game.player.action_part != null:
        var pump_contact: Vector3 = game.player.action_part.transform * pump_socket
        var pump_palm_position: Vector3 = game.player.viewmodel_root.to_local(pump_palm.global_position)
        _expect(pump_contact.distance_to(pump_palm_position) < 0.12,
            "shotgun support palm must stay on the moving pump grip")
    game.player.reloading = false
    game.player.reload_elapsed = 0.0
    game.player._animate_viewmodel(0.20, 0.0)
    _expect(game.player.left_hand_rig.position.length() < 0.02,
        "shotgun support hand did not return after reload")
    # Articulated arm hierarchy: no disconnected elbow/hand geometry during
    # recoil, equip, reload, and the weapon-specific support hand animations.
    for gun_id: String in ["pistol", "smg", "rifle", "shotgun", "lmg"]:
        game.player.equip(gun_id)
        var shoulder_joint := game.player.hand_rig.get_node_or_null("TriggerShoulder") as Node3D
        var elbow_joint := shoulder_joint.get_node_or_null("Elbow") as Node3D if shoulder_joint != null else null
        var wrist_joint := elbow_joint.get_node_or_null("Wrist") as Node3D if elbow_joint != null else null
        _expect(shoulder_joint != null and elbow_joint != null and wrist_joint != null,
            "trigger arm hierarchy is incomplete for " + gun_id)
        if wrist_joint != null:
            _expect(wrist_joint.get_node_or_null("Palm") != null
                and wrist_joint.get_node_or_null("Finger0Joint/Finger0Proximal") != null
                and wrist_joint.get_node_or_null("Finger0Joint/Finger0TipJoint/Finger0Distal") != null
                and wrist_joint.get_node_or_null("ThumbJoint/ThumbProximal") != null
                and wrist_joint.get_node_or_null("ThumbJoint/ThumbTipJoint/ThumbDistal") != null,
                "gloved fingers/knuckles are incomplete for " + gun_id)
        if gun_id != "pistol":
            _expect(game.player.support_elbow_joint != null and game.player.support_wrist_joint != null,
                "support arm missing its independent articulated joints for " + gun_id)
        else:
            _expect(game.player.support_elbow_joint == null and game.player.support_wrist_joint == null,
                "pistol should not create an unused support arm rig")
        game.player.shot_anim = 0.7
        game.player.equip_anim_timer = 0.16
        game.player._animate_viewmodel(0.10, 0.0)
        _expect(game.player.trigger_elbow_joint != null
            and absf(game.player.trigger_elbow_joint.rotation.x) > 0.001,
            "trigger elbow is not animated by recoil/equip for " + gun_id)
        game.player.shot_anim = 0.0
        game.player.equip_anim_timer = 0.0
        game.player._animate_viewmodel(0.25, 0.0)
        _expect(absf(game.player.trigger_elbow_joint.rotation.x) < 0.015,
            "trigger elbow must return to neutral without animation drift for " + gun_id)
    # Hinged glove fingers: every weapon has four trigger-side pairs.
    # Only long guns expose the support hand. A rifle mag change opens its
    # fingers, and releasing the magazine closes the grip again.
    for finger_gun: String in ["pistol", "smg", "rifle", "shotgun", "lmg"]:
        game.player.equip(finger_gun)
        _expect(game.player.trigger_finger_knuckles.size() == 4
            and game.player.trigger_finger_tips.size() == 4,
            "trigger glove joints missing for " + finger_gun)
        _expect(game.player.support_finger_knuckles.size() == (0 if finger_gun == "pistol" else 4),
            "support glove joints missing or leaking after swap " + finger_gun)
        game.player.reloading = false
        game.player.equip_anim_timer = 0.0
        game.player.shot_anim = 0.0
        game.player._animate_viewmodel(0.25, 0.0)
        var trigger_rest: float = game.player.trigger_finger_knuckles[1].rotation.x
        game.player.shot_anim = 1.0
        game.player._animate_viewmodel(0.25, 0.0)
        _expect(game.player.trigger_finger_knuckles[1].rotation.x > trigger_rest + 0.15,
            "index finger must curl when firing " + finger_gun)
        game.player.shot_anim = 0.0
        game.player._animate_viewmodel(0.25, 0.0)
        _expect(absf(game.player.trigger_finger_knuckles[1].rotation.x - trigger_rest) < 0.015,
            "index finger must relax after firing " + finger_gun)
    game.player.equip("rifle")
    game.player.shot_anim = 0.0
    game.player.reloading = false
    game.player._animate_viewmodel(0.25, 0.0)
    var support_rest: float = game.player.support_finger_knuckles[1].rotation.x
    var support_tip_rest: float = game.player.support_finger_tips[1].rotation.x
    game.player.reloading = true
    game.player.reload_elapsed = float(reload_specs["rifle"]["reload"]) * 0.45
    game.player._animate_viewmodel(0.25, 0.0)
    _expect(game.player.support_finger_knuckles[1].rotation.x < support_rest - 0.12
        and game.player.support_finger_tips[1].rotation.x < support_tip_rest - 0.15,
        "support fingers must open to release the rifle magazine")
    game.player.reloading = false
    game.player.reload_elapsed = 0.0
    game.player._animate_viewmodel(0.25, 0.0)
    _expect(absf(game.player.support_finger_knuckles[1].rotation.x - support_rest) < 0.015,
        "support fingers must close after reloading")
    # Hinged thumbs on the five weapon classes: firing and magazine grasp.
    for thumb_gun: String in ["pistol", "smg", "rifle", "shotgun", "lmg"]:
        game.player.equip(thumb_gun)
        _expect(game.player.trigger_thumb_joint != null and game.player.trigger_thumb_tip_joint != null,
            "trigger thumb pivots missing for " + thumb_gun)
        _expect((game.player.support_thumb_joint != null) == (thumb_gun != "pistol"),
            "support thumb pivot should only exist for long guns " + thumb_gun)
        game.player.reloading = false
        game.player.shot_anim = 0.0
        game.player._animate_viewmodel(0.25, 0.0)
        var thumb_rest: float = game.player.trigger_thumb_joint.rotation.y
        game.player.shot_anim = 1.0
        game.player._animate_viewmodel(0.25, 0.0)
        _expect(game.player.trigger_thumb_joint.rotation.y < thumb_rest - 0.035,
            "trigger thumb must react to firing " + thumb_gun)
        game.player.shot_anim = 0.0
        game.player._animate_viewmodel(0.25, 0.0)
        _expect(absf(game.player.trigger_thumb_joint.rotation.y - thumb_rest) < 0.015,
            "trigger thumb must return to the grip " + thumb_gun)
    game.player.equip("rifle")
    game.player.reloading = false
    game.player._animate_viewmodel(0.25, 0.0)
    var support_thumb_rest: float = game.player.support_thumb_joint.rotation.y
    game.player.reloading = true
    game.player.reload_elapsed = float(reload_specs["rifle"]["reload"]) * 0.45
    game.player._animate_viewmodel(0.25, 0.0)
    _expect(game.player.support_thumb_joint.rotation.y > support_thumb_rest + 0.15,
        "support thumb must release the magazine grip during reload")
    game.player.reloading = false
    game.player.reload_elapsed = 0.0
    game.player._animate_viewmodel(0.25, 0.0)
    _expect(absf(game.player.support_thumb_joint.rotation.y - support_thumb_rest) < 0.015,
        "support thumb must close after magazine insertion")
    # Recoil is visually distinct by weapon class without modifying combat damage.
    var observed_visual_kick: Dictionary = {}
    for recoil_gun: String in ["smg", "pistol", "rifle", "lmg", "shotgun"]:
        game.player.equip(recoil_gun)
        game.player.aim = false
        game.player.reloading = false
        game.player.melee_anim_timer = 0.0
        game.player.equip_anim_timer = 0.0
        game.player.idle_clock = 0.0
        game.player.walk_anim_blend = 0.0
        game.player.shot_anim = 1.0
        game.player._animate_viewmodel(0.25, 0.0)
        observed_visual_kick[recoil_gun] = game.player.viewmodel_root.position.z
        _expect(observed_visual_kick[recoil_gun] > 0.04,
            "weapon recoil must visibly move the first-person model " + recoil_gun)
        game.player.shot_anim = 0.0
        game.player._animate_viewmodel(0.25, 0.0)
        _expect(absf(game.player.viewmodel_root.position.z) < 0.005,
            "weapon should return to resting pose after recoil " + recoil_gun)
    _expect(observed_visual_kick["shotgun"] > observed_visual_kick["lmg"]
        and observed_visual_kick["lmg"] > observed_visual_kick["rifle"]
        and observed_visual_kick["rifle"] > observed_visual_kick["pistol"]
        and observed_visual_kick["pistol"] > observed_visual_kick["smg"],
        "weapon classes must have visibly different recoil amplitudes")
    # Player-initiated weapon switch should lower the OLD model before it swaps.
    # Forced shop/loot/recovery equip remains immediate and cancels pending changes.
    game.player.equip("rifle")
    var outgoing_weapon_root: Node3D = game.player.viewmodel_root
    game.player.magazines["rifle"] = 8
    game.player.reserves["rifle"] = 24
    game.player.reloading = true
    game.player.switch_weapon("pistol")
    _expect(game.player.weapon_id == "rifle" and game.player.pending_weapon_id == "pistol"
        and game.player.holster_timer > 0.0 and not game.player.reloading,
        "manual swap must holster before replacing the model and cancel reload")
    game.player._advance_weapon_switch(0.10)
    game.player._animate_viewmodel(0.20, 0.0)
    _expect(game.player.weapon_id == "rifle" and game.player.viewmodel_root == outgoing_weapon_root
        and game.player.viewmodel_root.position.y < -0.08,
        "outgoing gun should visibly lower while the old model remains mounted")
    var magazine_before_swap: int = game.player.magazines["rifle"]
    game.player.shoot()
    game.player.start_reload()
    _expect(game.player.magazines["rifle"] == magazine_before_swap and not game.player.reloading,
        "switching blocks fire/reload while waiting for the incoming model")
    game.player._advance_weapon_switch(0.11)
    _expect(game.player.weapon_id == "pistol" and game.player.pending_weapon_id == ""
        and game.player.equip_anim_timer > 0.0 and game.player.viewmodel_root != outgoing_weapon_root,
        "incoming pistol should equip only after old gun is lowered")
    game.player.switch_weapon("rifle")
    game.player.equip("smg")
    _expect(game.player.weapon_id == "smg" and game.player.pending_weapon_id == ""
        and game.player.holster_timer == 0.0,
        "forced equip must cancel a queued manual weapon switch")
    game.player.switch_weapon("pistol")
    game.player.switch_weapon("smg")
    _expect(game.player.weapon_id == "smg" and game.player.pending_weapon_id == "",
        "selecting the currently equipped gun should cancel a pending holster")
    game.player.equip("rifle")
    game.player.idle_clock = PI * 0.3125
    game.player.walk_anim_blend = 0.0
    game.player.shot_anim = 0.0
    game.player.equip_anim_timer = 0.0
    game.player._animate_viewmodel(0.25, 0.0)
    var idle_height: float = game.player.viewmodel_root.position.y
    game.player.walk_anim_blend = 1.0
    game.player.walk_clock = PI * 0.5
    game.player._animate_viewmodel(0.25, 0.0)
    _expect(absf(game.player.viewmodel_root.position.y - idle_height) > 0.004,
        "walking should produce controlled viewmodel bob separate from idle breathing")
    game.player.walk_anim_blend = 0.0
    game.player.walk_clock = 0.0
    # Geometry sanity: glove palms must stay ahead of camera near plane,
    # while remaining inside a conservative FPS framing envelope.
    for gun_id: String in ["pistol", "smg", "rifle", "shotgun", "lmg"]:
        game.player.equip(gun_id)
        var palm_node := game.player.hand_rig.get_node_or_null("TriggerShoulder/Elbow/Wrist/Palm") as Node3D
        _expect(palm_node != null, "trigger palm missing from FPS visual rig " + gun_id)
        if palm_node != null:
            var palm_local: Vector3 = game.player.camera.to_local(palm_node.global_position)
            _expect(palm_local.z < -0.10 and absf(palm_local.x) < 1.3
                and absf(palm_local.y) < 1.3,
                "trigger glove is behind camera or outside FPS framing for " + gun_id)
        if gun_id != "pistol":
            var support_palm := game.player.left_hand_rig.get_node_or_null("SupportShoulder/Elbow/Wrist/Palm") as Node3D
            _expect(support_palm != null, "support palm missing from FPS rig " + gun_id)
            if support_palm != null:
                var support_local: Vector3 = game.player.camera.to_local(support_palm.global_position)
                _expect(support_local.z < -0.10 and absf(support_local.x) < 1.3
                    and absf(support_local.y) < 1.3,
                    "support glove is behind camera or outside FPS framing for " + gun_id)
    # Real world-collision regression: a short wall should fold a long gun
    # without moving the camera, changing fire range, or hiding the world.
    game.player.equip("rifle")
    var wall_probe := StaticBody3D.new()
    wall_probe.collision_layer = 1
    wall_probe.collision_mask = 0
    var wall_collision := CollisionShape3D.new()
    var wall_shape := BoxShape3D.new()
    wall_shape.size = Vector3(1.6, 1.5, 0.12)
    wall_collision.shape = wall_shape
    wall_probe.add_child(wall_collision)
    game.add_child(wall_probe)
    # Match the camera basis so the thin wall faces its ray even when the
    # player has turned sideways; the ray must not start inside the box.
    wall_probe.global_transform = Transform3D(game.player.camera.global_transform.basis,
        game.player.camera.global_position - game.player.camera.global_transform.basis.z * 0.62)
    await physics_frame
    var rifle_wall_tuck: float = game.player._weapon_wall_proximity()
    var probe_from: Vector3 = game.player.camera.global_position
    var probe_direction: Vector3 = -game.player.camera.global_transform.basis.z
    var wall_query := PhysicsRayQueryParameters3D.create(probe_from, probe_from + probe_direction * 1.25)
    wall_query.collision_mask = 1
    wall_query.exclude = [game.player.get_rid()]
    var wall_hit: Dictionary = game.player.get_world_3d().direct_space_state.intersect_ray(wall_query)
    _expect(not wall_hit.is_empty() and wall_hit.get("collider") == wall_probe,
        "weapon ray must collide with the physical wall fixture")
    var wall_distance: float = probe_from.distance_to(wall_hit["position"]) if not wall_hit.is_empty() else INF
    var expected_tuck: float = clampf((1.25 - wall_distance) / 0.70, 0.0, 1.0)
    # The player collision solver may shift the camera away from the fixture
    # after a physics frame, so use the actual hit distance instead of assuming
    # that a wall placed at 0.62 m stays at a constant camera-relative distance.
    _expect(rifle_wall_tuck > 0.25 and absf(rifle_wall_tuck - expected_tuck) < 0.02,
        "nearby wall must tuck the long gun before muzzle clipping")
    game.player.equip("pistol")
    _expect(game.player._weapon_wall_proximity() < rifle_wall_tuck,
        "pistol should need less wall clearance than the long gun")
    wall_probe.queue_free()
    await physics_frame
    game.player.equip("rifle")
    _expect(game.player._weapon_wall_proximity() < 0.05,
        "wall tuck must release when a physical obstruction is removed")
    game.player.weapon_wall_blend = 0.0
    game.player.equip_anim_timer = 0.0
    game.player.equip("pistol")
    _expect(game.player.left_hand_rig.get_child_count() == 0,
        "pistol must not render a floating support hand")
    game.player.switch_weapon(starting_weapon, true)
    game.player.last_primary = saved_primary
    game.player.grenade_throw_timer = saved_grenade_timer

    var stations: Array[Vector3] = []
    for station in game.shops:
        stations.append(station["position"])
    var points: Array[Vector3] = [
        Vector3(-22, 1.5, -22), Vector3(0, 1.5, -23), Vector3(22, 1.5, -22),
        Vector3(-23, 1.5, 0), Vector3(23, 1.5, 0),
        Vector3(-22, 1.5, 22), Vector3(0, 1.5, 23), Vector3(22, 1.5, 22)
    ]
    var good_spawns: int = 0
    for i in range(100):
        var result: Dictionary = SpawnSelector.select_position(
            points, stations, game.get_world_3d().direct_space_state,
            game.player.global_position, Vector3.FORWARD
        )
        if result.get("valid", false):
            good_spawns += 1
            var spot: Vector3 = result["position"]
            _expect(spot.distance_to(game.player.global_position) >= 10.0, "spawn too close to player")
            for station in stations:
                _expect(Vector2(spot.x, spot.z).distance_to(Vector2(station.x, station.z)) >= 4.75, "spawn too close to shop")
    _expect(good_spawns == 100, "100 test spawns are valid")
    # In addition to sampling the center, move the logical player near every
    # edge point. The selected location must still be safely distant.
    for test_position in points:
        var edge_result: Dictionary = SpawnSelector.select_position(
            points, stations, game.get_world_3d().direct_space_state,
            test_position, Vector3.RIGHT
        )
        _expect(edge_result.get("valid", false), "spawn fails with player on an edge")
        if edge_result.get("valid", false):
            _expect(edge_result["position"].distance_to(test_position) >= 10.0,
                "edge player received a spawn too close")
    var no_safe: Dictionary = SpawnSelector.select_position(
        points, points, game.get_world_3d().direct_space_state,
        game.player.global_position, Vector3.FORWARD
    )
    _expect(not no_safe.get("valid", true), "all guarded points must reject spawning")
    var blocked: Array[Vector3] = [game.player.global_position]
    var rejected: Dictionary = SpawnSelector.select_position(
        blocked, stations, game.get_world_3d().direct_space_state,
        game.player.global_position, Vector3.FORWARD
    )
    _expect(not rejected.get("valid", true), "overlapping player spawn must be rejected")

    # Run waves with real enemy scenes, but eliminate them immediately to
    # avoid long unattended combat. This tests counters and reward signal.
    for wave_number in [1, 2]:
        game._begin_wave()
        _expect(game.wave == wave_number, "incorrect wave number")
        _expect(game.phase == "wave", "wave did not enter combat")
        var original_total: int = game.spawn_remaining
        var spawned_count: int = 0
        var attempts: int = 0
        while game.spawn_remaining > 0 and attempts < 150:
            await physics_frame
            attempts += 1
            # Existing automatic spawns are also included in the kill count.
            for enemy in get_nodes_in_group("enemies"):
                if is_instance_valid(enemy) and not enemy.dead:
                    enemy.take_damage(100000.0)
                    spawned_count += 1
            if game.spawn_remaining > 0 and game.alive < 12:
                game._spawn_enemy()
        for enemy in get_nodes_in_group("enemies"):
            if is_instance_valid(enemy) and not enemy.dead:
                enemy.take_damage(100000.0)
                spawned_count += 1
        await physics_frame
        await physics_frame
        _expect(attempts < 150, "wave spawn queue did not drain")
        _expect(game.alive == 0 and game.spawn_remaining == 0, "wave bookkeeping leak")
        _expect(game.phase == "break", "wave did not return to preparation")
        _expect(game.wave == wave_number, "wave number changed unexpectedly")
        _expect(game.wave_kills == original_total, "not every enemy kill was counted once")
        _expect(spawned_count == original_total, "spawn count mismatch")
        _expect(game.break_remaining > 0.0, "preparation timer missing")
    # Test the 10th-wave entry against the real HUD and scene state; a longer
    # 50-wave composition simulation runs separately without expensive NPCs.
    game.wave = 9
    game._begin_wave()
    _expect(game.wave == 10, "milestone wave number incorrect")
    _expect(game.spawn_remaining == 25, "milestone wave enemy budget changed")
    _expect(not game.player.aim or game.player.optic_reticle == null or not game.player.optic_reticle.visible,
        "scope reticle should not appear before ADS is completed")
    _expect(game.banner_title.contains("BLINDADA"), "armored wave lacks HUD warning")
    game.queue_free()
    await process_frame
    if failures.is_empty():
        print("QA_RUNTIME_PASS %d assertions, 100 spawn samples, 2 wave transitions, armed allies and vertex materials" % checked)
        quit(0)
    else:
        print("QA_RUNTIME_FAIL %s" % str(failures))
        quit(1)


func _matches_source_pcm(clip: AudioStreamWAV) -> bool:
    if clip == null or clip.format != AudioStreamWAV.FORMAT_16_BITS:
        return false
    var source := FileAccess.get_file_as_bytes(clip.resource_path)
    # Project WAVs are written as PCM with a canonical 44-byte header.
    if source.size() < 44 or source.slice(36, 40).get_string_from_ascii() != "data":
        return false
    return clip.data == source.slice(44)
