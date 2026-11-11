extends CharacterBody3D
class_name SurvivalPlayer

const GunMaterials = preload("res://scripts/weapon_materials.gd")
const WeaponAudio = preload("res://scripts/weapon_audio.gd")

signal grenade_requested
signal hit_confirmed
signal shot_resolved(hit_enemy: bool, was_headshot: bool)
signal downed_started
signal downed_recovered
signal headshot_confirmed
signal shot_fired(at: Vector3, hit_enemy: bool)
signal player_died
signal damage_received(source_position: Vector3, damage: float)

const PERKS := {
    "quick_reload": "RECARGA AGIL",
    "steady": "MIRA FIRME",
    "fast_ads": "REACAO RAPIDA",
    "mobility": "MOBILIDADE",
    "resistance": "RESISTENCIA"
}
const WEAPONS = {
    "pistol": {"name":"Pistola", "damage":30.0, "mag":15, "reserve":90, "rate":0.20, "reload":1.25, "spread":0.008, "auto":false, "pellets":1},
    "smg": {"name":"Submetralhadora", "damage":19.0, "mag":32, "reserve":160, "rate":0.085, "reload":1.70, "spread":0.023, "auto":true, "pellets":1},
    "rifle": {"name":"Fuzil", "damage":34.0, "mag":30, "reserve":150, "rate":0.13, "reload":1.95, "spread":0.011, "auto":true, "pellets":1},
    "shotgun": {"name":"Escopeta", "damage":17.0, "mag":8, "reserve":48, "rate":0.72, "reload":2.15, "spread":0.09, "auto":false, "pellets":8},
    "lmg": {"name":"Metralhadora leve", "damage":28.0, "mag":75, "reserve":225, "rate":0.105, "reload":3.65, "spread":0.018, "auto":true, "pellets":1}
}

var camera: Camera3D
var gun: Node3D
var weapon_model: Node3D
var viewmodel_root: Node3D
var hand_rig: Node3D
var viewmodel_depth: float = 0.0
var viewmodel_scale: float = 0.95
var magazine_part: Node3D
var action_part: Node3D
var reload_elapsed: float = 0.0
var equip_anim_timer: float = 0.0
var shot_anim: float = 0.0
var melee_anim_timer: float = 0.0
var damage_anim: float = 0.0
var melee_timer: float = 0.0
var muzzle_flash: MeshInstance3D
var shot_sound: AudioStreamPlayer
var reload_sound: AudioStreamPlayer
var weapon_id: String = "pistol"
var magazines: Dictionary = {}
var reserves: Dictionary = {}
var health: float = 100.0
var armor: float = 0.0
var upgrades: int = 0
var dead: bool = false
var controls_locked: bool = false
var fire_timer: float = 0.0
var reload_timer: float = 0.0
var flash_timer: float = 0.0
var reloading: bool = false
var aim: bool = false
var recoil: float = 0.0
var walk_clock: float = 0.0
var last_primary: String = ""
var previous_weapon: String = "pistol"
var owned_weapons: Array[String] = ["pistol"]
var weapon_upgrades: Dictionary = {}
var shot_spread_kick: float = 0.0
var sprint_blend: float = 0.0
var left_hand_rig: Node3D
var active_arm_parent: Node3D
var invulnerability_timer: float = 0.0
var collider_node: CollisionShape3D
var capsule_shape: CapsuleShape3D
var posture: String = "stand"
var prone_requested: bool = false
var camera_stand_height: float = 0.64
var current_body_height: float = 1.8
var active_perk: String = ""
var weapon_attachments: Dictionary = {}
var downed: bool = false
var downed_seconds: float = 0.0
var last_stand_available: bool = true
var self_revive_kits: int = 0
var shot_serial: int = 0

func _ready() -> void:
    collision_layer = 2
    collision_mask = 1
    var collider := CollisionShape3D.new()
    var capsule := CapsuleShape3D.new()
    capsule.radius = 0.35
    capsule.height = 1.8
    collider.shape = capsule
    collider_node = collider
    capsule_shape = capsule
    add_child(collider)
    camera = Camera3D.new()
    camera.position = Vector3(0, 0.64, 0)
    camera.fov = GameSettings.field_of_view
    camera.current = true
    add_child(camera)
    gun = Node3D.new()
    gun.position = Vector3(0.32, -0.28, -0.65)
    camera.add_child(gun)
    muzzle_flash = MeshInstance3D.new()
    muzzle_flash.mesh = _build_muzzle_flash()
    var flash_mat := StandardMaterial3D.new()
    flash_mat.albedo_color = Color(1.0, 0.82, 0.42)
    flash_mat.emission_enabled = true
    flash_mat.emission = Color(1.0, 0.60, 0.20)
    flash_mat.emission_energy_multiplier = 2.0
    flash_mat.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
    flash_mat.cull_mode = BaseMaterial3D.CULL_DISABLED
    muzzle_flash.material_override = flash_mat
    muzzle_flash.visible = false
    gun.add_child(muzzle_flash)
    shot_sound = AudioStreamPlayer.new()
    shot_sound.volume_db = -6.0
    shot_sound.max_polyphony = 8
    shot_sound.bus = "SFX"
    add_child(shot_sound)
    reload_sound = AudioStreamPlayer.new()
    reload_sound.volume_db = -14.0
    reload_sound.bus = "SFX"
    add_child(reload_sound)
    for id in WEAPONS:
        magazines[id] = WEAPONS[id]["mag"]
        reserves[id] = WEAPONS[id]["reserve"]
        weapon_upgrades[id] = 0
        weapon_attachments[id] = {"optic": "", "muzzle": ""}
    _update_gun_mesh()
    _update_shot_audio()
    Input.set_mouse_mode(Input.MOUSE_MODE_CAPTURED)

func _can_expand_to_height(target_height: float) -> bool:
    var probe := CapsuleShape3D.new()
    probe.radius = 0.35
    probe.height = target_height
    var params := PhysicsShapeQueryParameters3D.new()
    params.shape = probe
    params.transform = Transform3D(global_transform.basis,
        global_position + Vector3(0.0, (target_height - 1.8) * 0.5, 0.0))
    params.exclude = [get_rid()]
    params.collision_mask = 1
    return get_world_3d().direct_space_state.intersect_shape(params, 1).is_empty()

func _update_posture(delta: float, crouch_pressed: bool) -> void:
    var desired_state := "downed" if downed else ("prone" if prone_requested else ("crouch" if crouch_pressed else "stand"))
    var desired_height := 0.75 if desired_state in ["downed", "prone"] else (1.18 if desired_state == "crouch" else 1.8)
    if desired_height > current_body_height + 0.025 and not _can_expand_to_height(desired_height):
        # Stand-up is rejected under a low roof, so the capsule never phases
        # through overhead geometry.
        desired_state = posture
        desired_height = current_body_height
    posture = desired_state
    current_body_height = move_toward(current_body_height, desired_height, delta * 3.6)
    capsule_shape.height = maxf(0.72, current_body_height)
    collider_node.position.y = (current_body_height - 1.8) * 0.5
    var sight_level: float = camera_stand_height + (current_body_height - 1.8) * 0.88
    camera.position.y = lerpf(camera.position.y, sight_level, minf(1.0, delta * 12.0))

func has_attachment(slot: String, id: String) -> bool:
    return str(weapon_attachments.get(weapon_id, {}).get(slot, "")) == id

func install_attachment(slot: String, id: String) -> bool:
    if slot == "optic" and id not in ["red_dot", "holo"]:
        return false
    if slot == "muzzle" and id not in ["suppressor", "compensator"]:
        return false
    var selections: Dictionary = weapon_attachments.get(weapon_id, {"optic":"", "muzzle":""})
    if selections.get(slot, "") == id:
        return false
    selections[slot] = id
    weapon_attachments[weapon_id] = selections
    _update_gun_mesh()
    _update_shot_audio()
    return true

func select_perk(id: String) -> bool:
    if not PERKS.has(id) or active_perk == id:
        return false
    active_perk = id
    return true

func recover_downed(using_kit: bool = false) -> void:
    if not downed or dead:
        return
    downed = false
    downed_seconds = 0.0
    prone_requested = false
    health = 35.0 if not using_kit else 50.0
    invulnerability_timer = 1.3
    if last_primary != "" and owned_weapons.has(last_primary):
        switch_weapon(last_primary, true)
    downed_recovered.emit()

func _die_finally() -> void:
    downed = false
    dead = true
    reload_sound.stop()
    controls_locked = true
    if not GameSettings.training_respawns:
        Input.set_mouse_mode(Input.MOUSE_MODE_VISIBLE)
    player_died.emit()

func _physics_process(delta: float) -> void:
    if dead:
        return
    fire_timer = maxf(fire_timer - delta, 0.0)
    if downed:
        downed_seconds -= delta
        if downed_seconds <= 0.0:
            if self_revive_kits > 0:
                self_revive_kits -= 1
                recover_downed(true)
            else:
                _die_finally()
                return
    melee_timer = maxf(melee_timer - delta, 0.0)
    invulnerability_timer = maxf(0.0, invulnerability_timer - delta)
    flash_timer = maxf(flash_timer - delta, 0.0)
    equip_anim_timer = maxf(0.0, equip_anim_timer - delta)
    shot_anim = maxf(0.0, shot_anim - delta * 13.5)
    melee_anim_timer = maxf(0.0, melee_anim_timer - delta)
    damage_anim = maxf(0.0, damage_anim - delta * 3.4)
    muzzle_flash.visible = flash_timer > 0.0
    if reloading:
        reload_elapsed += delta
        reload_timer -= delta
        if reload_timer <= 0.0:
            _finish_reload()
    if not is_on_floor():
        velocity.y -= 22.0 * delta
    elif velocity.y < 0.0:
        velocity.y = -0.2
    var movement := Vector2.ZERO
    if not controls_locked:
        if Input.is_key_pressed(KEY_W): movement.y -= 1.0
        if Input.is_key_pressed(KEY_S): movement.y += 1.0
        if Input.is_key_pressed(KEY_A): movement.x -= 1.0
        if Input.is_key_pressed(KEY_D): movement.x += 1.0
    movement = movement.normalized()
    var crouching := (Input.is_key_pressed(KEY_C) or Input.is_key_pressed(KEY_CTRL)) and not controls_locked
    _update_posture(delta, crouching)
    var sprinting := Input.is_key_pressed(KEY_SHIFT) and movement.y < -0.05 and posture == "stand" and not downed and not reloading and not controls_locked
    sprint_blend = move_toward(sprint_blend, 1.0 if sprinting else 0.0, delta * (5.0 if sprinting else 7.5))
    aim = Input.is_mouse_button_pressed(MOUSE_BUTTON_RIGHT) and not controls_locked and sprint_blend < 0.20 and not downed
    var speed := 0.8 if downed else (1.15 if posture == "prone" else (2.8 if posture == "crouch" else (8.0 if sprinting else (4.35 if aim else 5.2))))
    if active_perk == "mobility" and aim:
        speed *= 1.17
    var world_move := global_transform.basis * Vector3(movement.x, 0, movement.y)
    velocity.x = move_toward(velocity.x, world_move.x * speed, delta * 24.0)
    velocity.z = move_toward(velocity.z, world_move.z * speed, delta * 24.0)
    if Input.is_key_pressed(KEY_SPACE) and is_on_floor() and posture == "stand" and not downed and not controls_locked:
        velocity.y = 6.5
    move_and_slide()
    # A slight sprint FOV extension sells momentum; ADS always takes priority.
    var target_fov: float = GameSettings.field_of_view * (0.70 if aim else (1.045 if sprint_blend > 0.55 else 1.0))
    camera.fov = lerpf(camera.fov, target_fov, minf(1.0, delta * (14.0 if active_perk == "fast_ads" else 10.0)))
    walk_clock += delta * movement.length() * (12.0 if sprinting else 8.0)
    shot_spread_kick = move_toward(shot_spread_kick, 0.0, delta * 1.25)
    # Align the physical front/rear sight with the camera's central ray.
    # No on-screen crosshair: the actual sight must indicate point of aim.
    var sight_height: float = float({"pistol": 0.121, "smg": 0.232, "rifle": 0.177, "shotgun": 0.140, "lmg": 0.232}.get(weapon_id, 0.20))
    var sight_y := -viewmodel_scale * sight_height
    var gun_target := Vector3(0.0, sight_y, -0.62) if aim else Vector3(0.34, -0.27, -0.63)
    # A true tactical sprint: lower the rifle, pitch the muzzle down and
    # let the support arm drop. Smooth transitions prevent camera popping.
    var running_bob := sin(walk_clock) * 0.029 * sprint_blend
    gun_target.y += sin(walk_clock) * 0.007 * movement.length()
    gun_target = gun_target.lerp(Vector3(0.49, -0.50 + running_bob, -0.45), sprint_blend)
    recoil = move_toward(recoil, 0.0, delta * 2.0)
    if reloading:
        gun_target.y -= 0.21
        gun_target.x += 0.08
    gun_target.z += recoil
    gun.position = gun.position.lerp(gun_target, minf(1.0, delta * 13.0))
    var sway_strength := (0.006 if aim else 0.018) * movement.length()
    gun.rotation.z = lerpf(gun.rotation.z, -0.28 * sprint_blend + sin(walk_clock * 0.5) * (sway_strength + sprint_blend * 0.022), minf(1.0, delta * 11.0))
    gun.rotation.y = lerpf(gun.rotation.y, 0.14 * sprint_blend, minf(1.0, delta * 10.0))
    gun.rotation.x = lerpf(gun.rotation.x, -0.48 * sprint_blend + cos(walk_clock) * (sway_strength + sprint_blend * 0.035), minf(1.0, delta * 10.0))
    _animate_viewmodel(delta, sprinting)
    # Automáticas continuam disparando enquanto o botão permanece pressionado.
    if not controls_locked and Input.get_mouse_mode() == Input.MOUSE_MODE_CAPTURED:
        if Input.is_mouse_button_pressed(MOUSE_BUTTON_LEFT) and WEAPONS[weapon_id]["auto"]:
            shoot()

# _input recebe o clique antes de Control/UI. O tiro semiautomático não
# depende mais de _unhandled_input (que pode descartar o clique).
func _input(event: InputEvent) -> void:
    if event is InputEventMouseMotion and Input.get_mouse_mode() == Input.MOUSE_MODE_CAPTURED and not controls_locked and not dead:
        rotate_y(-event.relative.x * 0.002 * GameSettings.mouse_sensitivity)
        camera.rotate_x(-event.relative.y * 0.002 * GameSettings.mouse_sensitivity)
        camera.rotation.x = clampf(camera.rotation.x, -1.45, 1.45)
    if event is InputEventMouseButton and event.pressed:
        if event.button_index == MOUSE_BUTTON_LEFT and not dead and not controls_locked:
            if Input.get_mouse_mode() != Input.MOUSE_MODE_CAPTURED:
                Input.set_mouse_mode(Input.MOUSE_MODE_CAPTURED)
            shoot()
    if event is InputEventKey and event.pressed and not event.echo:
        if not dead and not controls_locked:
            if event.keycode == KEY_Z and not downed:
                prone_requested = not prone_requested
            if event.keycode == KEY_R:
                start_reload()
            elif event.keycode == KEY_G:
                grenade_requested.emit()
            elif event.keycode == KEY_E:
                melee()
            elif event.keycode == KEY_1 and last_primary != "":
                switch_weapon(last_primary)
            elif event.keycode == KEY_2:
                switch_weapon("pistol")
    if event is InputEventMouseButton and event.pressed and not dead and not controls_locked:
        if event.button_index == MOUSE_BUTTON_WHEEL_UP or event.button_index == MOUSE_BUTTON_WHEEL_DOWN:
            if weapon_id == "pistol" and last_primary != "":
                switch_weapon(last_primary)
            else:
                switch_weapon("pistol")

func shoot() -> void:
    if dead or controls_locked or reloading or sprint_blend > 0.22 or fire_timer > 0.0:
        return
    if downed and weapon_id != "pistol":
        return
    if magazines[weapon_id] <= 0:
        start_reload()
        return
    magazines[weapon_id] -= 1
    shot_serial += 1
    fire_timer = WEAPONS[weapon_id]["rate"]
    recoil = 0.13 if weapon_id == "shotgun" else (0.075 if weapon_id == "lmg" else 0.055)
    if has_attachment("muzzle", "compensator"):
        recoil *= 0.80
    shot_spread_kick = minf(0.015, shot_spread_kick + (0.0015 if has_attachment("muzzle", "compensator") else 0.002))
    var kick_degrees := 0.55 if weapon_id == "shotgun" else (0.22 if weapon_id == "smg" else 0.32)
    if aim:
        kick_degrees *= 0.78
    flash_timer = 0.047 if weapon_id != "shotgun" else 0.080
    shot_anim = 1.0
    muzzle_flash.visible = true
    shot_sound.play()
    var origin := camera.global_position
    var space := get_world_3d().direct_space_state
    var did_hit := false
    var did_headshot := false
    var pellet_count: int = WEAPONS[weapon_id]["pellets"]
    var spread: float = (WEAPONS[weapon_id]["spread"] + shot_spread_kick) * (0.35 if aim else 1.0)
    if active_perk == "steady":
        spread *= 0.75
    if posture == "crouch":
        spread *= 0.82
    elif posture == "prone":
        spread *= 0.65
    var impact_point := origin + (-camera.global_transform.basis.z) * 45.0
    for n in range(pellet_count):
        var forward := -camera.global_transform.basis.z
        var direction := (forward + camera.global_transform.basis.x * randf_range(-spread, spread) + camera.global_transform.basis.y * randf_range(-spread, spread)).normalized()
        var query := PhysicsRayQueryParameters3D.create(origin, origin + direction * 100.0)
        query.exclude = [get_rid()]
        query.collision_mask = 3
        var result := space.intersect_ray(query)
        if not result.is_empty():
            impact_point = result["position"]
            var target: Object = result["collider"]
            if target.has_method("take_damage"):
                var base_damage: float = WEAPONS[weapon_id]["damage"]
                var multiplier := 1.0
                if target is SurvivalEnemy and result["position"].y > target.global_position.y + 0.53:
                    multiplier = 1.75
                    did_headshot = true
                if target is SurvivalEnemy:
                    target.take_damage(base_damage * multiplier * (1.0 + 0.24 * upgrades), "player", multiplier > 1.0, shot_serial)
                    did_hit = true
                else:
                    target.take_damage(base_damage * multiplier * (1.0 + 0.24 * upgrades))
    shot_fired.emit(impact_point, did_hit)
    shot_resolved.emit(did_hit, did_headshot)
    # Recoil occurs AFTER the raycast so a first shot goes through the sight,
    # not through the already-kicked camera direction.
    camera.rotation.x = clampf(camera.rotation.x + deg_to_rad(kick_degrees), -1.45, 1.45)
    if did_hit:
        hit_confirmed.emit()
        if did_headshot:
            headshot_confirmed.emit()
    if magazines[weapon_id] == 0 and reserves[weapon_id] > 0:
        start_reload()

func melee() -> void:
    if dead or controls_locked or reloading or melee_timer > 0.0:
        return
    melee_timer = 0.65
    melee_anim_timer = 0.40
    fire_timer = maxf(fire_timer, 0.32)
    recoil = 0.14
    var origin := camera.global_position
    var direction := -camera.global_transform.basis.z
    var query := PhysicsRayQueryParameters3D.create(origin, origin + direction * 2.4)
    query.collision_mask = 3
    query.exclude = [get_rid()]
    var result := get_world_3d().direct_space_state.intersect_ray(query)
    if not result.is_empty():
        var target: Object = result["collider"]
        if target.has_method("take_damage"):
            target.take_damage(70.0)
            hit_confirmed.emit()

func start_reload() -> void:
    if reloading or magazines[weapon_id] >= WEAPONS[weapon_id]["mag"] or reserves[weapon_id] <= 0:
        return
    reloading = true
    reload_timer = WEAPONS[weapon_id]["reload"] * (0.80 if active_perk == "quick_reload" else 1.0)
    reload_elapsed = 0.0
    reload_sound.stop()
    reload_sound.play()

func _finish_reload() -> void:
    reloading = false
    var needed: int = WEAPONS[weapon_id]["mag"] - magazines[weapon_id]
    var loaded: int = mini(needed, reserves[weapon_id])
    magazines[weapon_id] += loaded
    reserves[weapon_id] -= loaded

func equip(id: String) -> void:
    if not WEAPONS.has(id):
        return
    if not owned_weapons.has(id):
        owned_weapons.append(id)
    if id != "pistol":
        last_primary = id
    switch_weapon(id, true)

func switch_weapon(id: String, force: bool = false) -> void:
    if dead or (controls_locked and not force) or not owned_weapons.has(id) or id == weapon_id:
        return
    previous_weapon = weapon_id
    weapon_upgrades[weapon_id] = upgrades
    weapon_id = id
    reloading = false
    reload_sound.stop()
    upgrades = int(weapon_upgrades.get(id, 0))
    fire_timer = 0.14
    shot_anim = 0.0
    reload_elapsed = 0.0
    _update_gun_mesh()
    _update_shot_audio()

func refill_ammo() -> void:
    reserves[weapon_id] = WEAPONS[weapon_id]["reserve"]
    magazines[weapon_id] = WEAPONS[weapon_id]["mag"]
    reloading = false
    reload_sound.stop()

func heal(amount: float) -> void:
    health = minf(100.0, health + amount)

func add_armor(amount: float) -> void:
    armor = minf(100.0, armor + amount)

func take_damage(amount: float, source_position: Vector3 = Vector3.ZERO) -> void:
    if dead or invulnerability_timer > 0.0:
        return
    if GameSettings.training_respawns:
        amount *= 0.68 # Campo de Testes prioriza experimentar sistemas, nao perder partidas.
    var absorbed := minf(armor, amount * 0.65)
    armor -= absorbed
    health = maxf(0.0, health - (amount - absorbed))
    damage_anim = minf(1.0, damage_anim + amount * 0.015)
    damage_received.emit(source_position, amount - absorbed)
    if health <= 0.0:
        dead = true
        reload_sound.stop()
        controls_locked = true
        if not GameSettings.training_respawns:
            Input.set_mouse_mode(Input.MOUSE_MODE_VISIBLE)
        player_died.emit()

func revive_for_testing() -> void:
    # Reanimacao sem reload: dinheiro, armas, pontuacao e onda continuam intactos.
    dead = false
    controls_locked = false
    health = 100.0
    armor = maxf(armor, 50.0)
    invulnerability_timer = 5.0
    position = Vector3(0, 1.7, 0)
    velocity = Vector3.ZERO
    fire_timer = 0.0
    reloading = false
    reload_elapsed = 0.0
    Input.set_mouse_mode(Input.MOUSE_MODE_CAPTURED)

func _piece(shape: Mesh, at: Vector3, metal_color: Color, angle: Vector3 = Vector3.ZERO) -> MeshInstance3D:
    var part := MeshInstance3D.new()
    part.mesh = shape
    part.position = at
    part.rotation = angle
    var material := StandardMaterial3D.new()
    material.albedo_color = metal_color
    material.metallic = 0.35
    material.roughness = 0.48
    part.material_override = material
    gun.add_child(part)
    return part

func _gun_box(at: Vector3, size: Vector3, color: Color, angle: Vector3 = Vector3.ZERO) -> void:
    var shape := BoxMesh.new()
    shape.size = size
    _piece(shape, at, color, angle)

func _gun_tube(at: Vector3, radius: float, height: float, color: Color, angle: Vector3 = Vector3.ZERO) -> void:
    var tube := CylinderMesh.new()
    tube.top_radius = radius
    tube.bottom_radius = radius
    tube.height = height
    _piece(tube, at, color, angle)

func _build_muzzle_flash() -> ArrayMesh:
    # Pequeno clarão em laminas pontudas, sem a antiga bola amarela.
    var st := SurfaceTool.new()
    st.begin(Mesh.PRIMITIVE_TRIANGLES)
    for i in range(6):
        var angle := float(i) * TAU / 6.0
        var side := Vector3(cos(angle), sin(angle), 0.0)
        var axis := Vector3(-sin(angle), cos(angle), 0.0)
        var tip := side * 0.022 + Vector3(0, 0, -0.21 if i % 2 == 0 else -0.11)
        st.add_vertex(axis * 0.027)
        st.add_vertex(-axis * 0.027)
        st.add_vertex(tip)
    return st.commit()

func _update_shot_audio() -> void:
    shot_sound.stream = WeaponAudio.shot_for(weapon_id)
    reload_sound.stream = WeaponAudio.reload_for(weapon_id)
    if has_attachment("muzzle", "suppressor"):
        if AudioServer.get_bus_index("SUPPRESSED") < 0:
            AudioServer.add_bus()
            var idx: int = AudioServer.bus_count - 1
            AudioServer.set_bus_name(idx, "SUPPRESSED")
            AudioServer.set_bus_send(idx, "SFX")
            var low_pass := AudioEffectLowPassFilter.new()
            low_pass.cutoff_hz = 1400.0
            AudioServer.add_bus_effect(idx, low_pass)
        # Real recorded weapon WAV routed through a low-pass effect. No
        # synthesizer or artificial beep is introduced.
        shot_sound.bus = "SUPPRESSED"
        shot_sound.volume_db = -14.0
    else:
        shot_sound.bus = "SFX"
        shot_sound.volume_db = -6.0

func _update_gun_mesh() -> void:
    for child in gun.get_children():
        if child != muzzle_flash:
            gun.remove_child(child)
            child.queue_free()
    magazine_part = null
    action_part = null
    weapon_model = null
    # Scale/depth avoid placing long stocks behind the camera's near plane.
    viewmodel_scale = float({"pistol": 0.95, "smg": 0.84, "rifle": 0.78, "shotgun": 0.70, "lmg": 0.74}.get(weapon_id, 0.84))
    viewmodel_depth = float({"pistol": 0.0, "smg": -0.14, "rifle": -0.24, "shotgun": -0.24, "lmg": -0.24}.get(weapon_id, -0.14))
    viewmodel_root = Node3D.new()
    viewmodel_root.name = "Viewmodel"
    gun.add_child(viewmodel_root)
    # Three lightweight mesh groups allow a visible magazine drop and a cycling bolt.
    # NPCs use the original merged GLB to keep rendering cost low.
    for part_name in ["body", "mag", "action"]:
        var path := "res://assets/models/%s_%s.glb" % [weapon_id, part_name]
        if not ResourceLoader.exists(path):
            continue
        var source: PackedScene = load(path)
        if source == null:
            continue
        var part := source.instantiate() as Node3D
        if part == null:
            continue
        part.name = part_name
        viewmodel_root.add_child(part)
        GunMaterials.apply_colors(part)
        part.scale = Vector3.ONE * viewmodel_scale
        part.position.z = viewmodel_depth
        if part_name == "mag":
            magazine_part = part
        elif part_name == "action":
            action_part = part
        else:
            weapon_model = part
    hand_rig = Node3D.new()
    hand_rig.name = "Hands"
    viewmodel_root.add_child(hand_rig)
    var long_gun := weapon_id != "pistol"
    var grip_z: float = viewmodel_depth + viewmodel_scale * (0.035 if weapon_id == "pistol" else 0.16)
    var support_z: float = viewmodel_depth + viewmodel_scale * float({"smg": -0.39, "rifle": -0.48, "shotgun": -0.43, "lmg": -0.55}.get(weapon_id, -0.40))
    active_arm_parent = hand_rig
    _add_first_person_arm(Vector3(0.30, -0.53, 0.52), Vector3(0.070, -0.18, grip_z), true)
    left_hand_rig = Node3D.new()
    left_hand_rig.name = "SupportArm"
    hand_rig.add_child(left_hand_rig)
    if long_gun:
        active_arm_parent = left_hand_rig
        _add_first_person_arm(Vector3(-0.36, -0.54, 0.37), Vector3(-0.075, -0.13, support_z), false)
    active_arm_parent = hand_rig
    var muzzle_z: float = viewmodel_depth + viewmodel_scale * float({"pistol": -0.29, "smg": -0.69, "rifle": -0.95, "shotgun": -1.04, "lmg": -1.13}.get(weapon_id, -0.69))
    var muzzle_height := float({"pistol": 0.061, "rifle": 0.039, "shotgun": 0.065}.get(weapon_id, 0.018))
    muzzle_flash.position = Vector3(0, viewmodel_scale * muzzle_height, muzzle_z)
    _build_attachment_models()
    equip_anim_timer = 0.34

func _build_attachment_models() -> void:
    var attach: Dictionary = weapon_attachments.get(weapon_id, {})
    var optic: String = str(attach.get("optic", ""))
    var muzzle: String = str(attach.get("muzzle", ""))
    if optic != "":
        var optic_root := Node3D.new()
        optic_root.name = "Attachment_Optic_" + optic
        viewmodel_root.add_child(optic_root)
        var sight_height: float = float({"pistol":0.121,"smg":0.232,"rifle":0.177,"shotgun":0.140,"lmg":0.232}.get(weapon_id, 0.18))
        var y: float = sight_height * viewmodel_scale
        var z: float = viewmodel_depth + (-0.11 if weapon_id == "pistol" else -0.08) * viewmodel_scale
        var sight := MeshInstance3D.new()
        var casing := BoxMesh.new()
        casing.size = Vector3(0.09, 0.095, 0.08)
        sight.mesh = casing
        sight.position = Vector3(0.0, y - 0.01, z)
        var mat := StandardMaterial3D.new()
        mat.albedo_color = Color(0.12, 0.15, 0.15)
        mat.roughness = 0.58
        sight.material_override = mat
        optic_root.add_child(sight)
        var glass := MeshInstance3D.new()
        var lens := SphereMesh.new()
        lens.radius = 0.024
        lens.height = 0.05
        glass.mesh = lens
        glass.position = Vector3(0.0, y + 0.028, z - 0.044)
        var glass_mat := StandardMaterial3D.new()
        glass_mat.albedo_color = Color(0.18, 0.43, 0.42, 0.75)
        glass_mat.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
        glass_mat.roughness = 0.2
        glass.material_override = glass_mat
        optic_root.add_child(glass)
    if muzzle != "":
        var tube := MeshInstance3D.new()
        tube.name = "Attachment_Muzzle_" + muzzle
        var cylinder := CylinderMesh.new()
        cylinder.top_radius = 0.033 if muzzle == "suppressor" else 0.044
        cylinder.bottom_radius = cylinder.top_radius
        cylinder.height = 0.30 if muzzle == "suppressor" else 0.11
        tube.mesh = cylinder
        tube.rotation.x = PI * 0.5
        var front_z: float = float({"pistol":-0.29,"smg":-0.69,"rifle":-0.95,"shotgun":-1.04,"lmg":-1.13}.get(weapon_id, -0.75))
        tube.position = Vector3(0.0, 0.04 * viewmodel_scale, viewmodel_depth + front_z * viewmodel_scale - cylinder.height * 0.48)
        var barrel_mat := StandardMaterial3D.new()
        barrel_mat.albedo_color = Color(0.12, 0.135, 0.14)
        barrel_mat.metallic = 0.55
        barrel_mat.roughness = 0.72
        tube.material_override = barrel_mat
        viewmodel_root.add_child(tube)
        if muzzle == "suppressor":
            muzzle_flash.visible = false

func _animate_viewmodel(delta: float, sprinting: bool) -> void:
    if not is_instance_valid(viewmodel_root) or not is_instance_valid(hand_rig):
        return
    var t := 0.0
    if reloading:
        var duration: float = WEAPONS[weapon_id]["reload"] * (0.80 if active_perk == "quick_reload" else 1.0)
        t = clampf(reload_elapsed / maxf(0.01, duration), 0.0, 1.0)
    var mag_out := 0.0
    if reloading and weapon_id != "shotgun":
        mag_out = smoothstep(0.12, 0.32, t) * (1.0 - smoothstep(0.61, 0.84, t))
    var pump := 0.0
    if reloading and weapon_id == "shotgun":
        pump = sin(t * PI * 2.0) * (0.12 if t > 0.45 else 0.0)
    var reload_tilt := sin(t * PI) if reloading else 0.0
    var equip_tilt := sin(clampf(equip_anim_timer / 0.34, 0.0, 1.0) * PI * 0.5)
    var melee_punch := sin((1.0 - melee_anim_timer / 0.40) * PI) if melee_anim_timer > 0.0 else 0.0
    var pos_target := Vector3(0.035 * reload_tilt, -0.075 * reload_tilt - 0.26 * equip_tilt - (0.04 if sprinting else 0.0), 0.085 * shot_anim - 0.22 * melee_punch)
    viewmodel_root.position = viewmodel_root.position.lerp(pos_target, minf(1.0, delta * 20.0))
    var rot_target := Vector3(0.09 * reload_tilt + 0.06 * shot_anim, 0.0, -0.20 * reload_tilt + 0.36 * melee_punch + 0.065 * damage_anim)
    viewmodel_root.rotation = viewmodel_root.rotation.lerp(rot_target, minf(1.0, delta * 17.0))
    if is_instance_valid(magazine_part):
        var mag_target := Vector3(0.06 * mag_out, -0.29 * mag_out, viewmodel_depth + 0.045 * mag_out)
        magazine_part.position = magazine_part.position.lerp(mag_target, minf(1.0, delta * 30.0))
        magazine_part.rotation.z = lerpf(magazine_part.rotation.z, 0.22 * mag_out, minf(1.0, delta * 27.0))
    if is_instance_valid(action_part):
        var cycling := 0.048 * shot_anim
        var rack := 0.055 * (sin(t * PI * 3.0) ** 2.0) if reloading and t > 0.67 else 0.0
        var action_target := Vector3(0, 0, viewmodel_depth + cycling + rack + pump)
        action_part.position = action_part.position.lerp(action_target, minf(1.0, delta * 26.0))
    var hand_target := Vector3(0.0, -0.07 * mag_out, 0.0)
    hand_rig.position = hand_rig.position.lerp(hand_target, minf(1.0, delta * 16.0))
    hand_rig.rotation.z = lerpf(hand_rig.rotation.z, 0.12 * mag_out, minf(1.0, delta * 15.0))
    if is_instance_valid(left_hand_rig):
        # Support hand releases the fore-end during sprint instead of being
        # glued to the weapon in an accelerated walking pose.
        left_hand_rig.position = left_hand_rig.position.lerp(
            # Arm comes down along the chest instead of remaining on the foregrip.
            Vector3(-0.12, -0.29 + sin(walk_clock * 0.5) * 0.032, 0.19) * sprint_blend,
            minf(1.0, delta * 11.0)
        )
        left_hand_rig.rotation.z = lerpf(
            left_hand_rig.rotation.z, -0.26 * sprint_blend, minf(1.0, delta * 11.0)
        )

func _arm_piece(shape: Mesh, at: Vector3, tint: Color, rotation: Vector3 = Vector3.ZERO) -> MeshInstance3D:
    var part := MeshInstance3D.new()
    part.mesh = shape
    part.position = at
    part.rotation = rotation
    var material := StandardMaterial3D.new()
    material.albedo_color = tint
    material.roughness = 0.84
    part.material_override = material
    active_arm_parent.add_child(part)
    return part

func _arm_link(start: Vector3, finish: Vector3, top_radius: float, bottom_radius: float, tint: Color) -> void:
    var direction := finish - start
    var segment := CylinderMesh.new()
    segment.top_radius = top_radius
    segment.bottom_radius = bottom_radius
    segment.height = direction.length()
    var part := _arm_piece(segment, (start + finish) * 0.5, tint)
    if direction.length() > 0.001:
        part.quaternion = Quaternion(Vector3.UP, direction.normalized())

func _add_first_person_arm(elbow: Vector3, wrist: Vector3, trigger_hand: bool) -> void:
    # Braco com manga e luva afuniladas, palma oval e dedos articulados.
    var uniform := Color(0.22, 0.29, 0.24)
    var cuff := Color(0.16, 0.21, 0.18)
    var glove := Color(0.095, 0.11, 0.12)
    _arm_link(elbow, wrist, 0.068, 0.112, uniform)
    _arm_link(wrist - Vector3(0, 0.038, 0), wrist + Vector3(0, 0.049, 0), 0.079, 0.075, cuff)
    var palm_location := wrist + Vector3(0, 0.045, -0.06)
    var palm := CapsuleMesh.new()
    palm.radius = 0.068
    palm.height = 0.18
    _arm_piece(palm, palm_location, glove, Vector3(PI * 0.5, 0, 0))
    for finger in range(4):
        var x: float = (float(finger) - 1.5) * 0.031
        var length := 0.11 if finger < 3 else 0.082
        _arm_link(palm_location + Vector3(x, -0.005, -0.068),
                  palm_location + Vector3(x, -0.052, -0.068 - length),
                  0.014, 0.020, glove)
    var sign_side := 1.0 if trigger_hand else -1.0
    _arm_link(palm_location + Vector3(sign_side * 0.051, 0.01, 0.010),
              palm_location + Vector3(sign_side * 0.093, -0.035, -0.066),
              0.021, 0.026, glove)
