extends Node3D

const SpawnSelector = preload("res://scripts/spawn_selector.gd")
const WaveRules = preload("res://scripts/wave_rules.gd")
const HitMarkerUI = preload("res://scripts/hit_marker.gd")
const BloodImpact = preload("res://scripts/blood_impact.gd")
const WorldPickup = preload("res://scripts/loot_pickup.gd")
const RoundStats = preload("res://scripts/survival_round_stats.gd")


const MAX_ACTIVE_ENEMIES := 12
const FragGrenade = preload("res://scripts/frag_grenade.gd")
const ENABLE_EXPERIMENTAL_HUMANOIDS := false
const MAX_CORPSES := 12
const MAX_LOOT := 18
const MAX_BLOOD_EFFECTS := 14
const INITIAL_PREPARATION_SECONDS := 25.0
const TEST_STARTING_CREDITS := 1200
const MAP_ID := "campo_de_testes"
const SHOP_OPTIONS := {
    "weapons": [
        ["Submetralhadora", 180, "smg"],
        ["Fuzil de assalto", 350, "rifle"],
        ["Escopeta", 450, "shotgun"],
        ["Metralhadora leve", 650, "lmg"],
        ["Mira Red Dot (arma atual)", 190, "red_dot"],
        ["Mira Holografica (arma atual)", 240, "holo"],
        ["Silenciador (arma atual)", 270, "suppressor"],
        ["Compensador (arma atual)", 180, "compensator"]
    ],
    "gear": [
        ["Repor municao", 80, "ammo"],
        ["+50 de colete", 130, "armor"],
        ["+50 de vida", 90, "medkit"],
        ["+2 granadas", 100, "grenades"],
        ["Melhoria de dano (+24%)", 220, "upgrade"],
        ["Kit de Reanimacao (1 uso)", 950, "self_revive"]
    ],
    "support": [
        ["Torreta automatica (115s)", 300, "turret"],
        ["Esquadrao aliado (2 soldados)", 420, "squad"],
        ["Ataque aereo tatico", 420, "airstrike"],
        ["Perk: Recarga Agil", 300, "perk_quick_reload"],
        ["Perk: Mira Firme", 300, "perk_steady"],
        ["Perk: Reacao Rapida", 300, "perk_fast_ads"],
        ["Perk: Mobilidade", 300, "perk_mobility"],
        ["Perk: Resistencia", 350, "perk_resistance"]
    ]
}

var player: SurvivalPlayer
var game_menu: SurvivalGameMenu
var wallet: int = TEST_STARTING_CREDITS
var grenades: int = 2
var ally_tokens: int = 0
var airstrike_tokens: int = 0
var wave: int = 0
var kills: int = 0
var record_wave: int = 0
var phase: String = "break"
var break_remaining: float = INITIAL_PREPARATION_SECONDS
var break_duration: float = INITIAL_PREPARATION_SECONDS
var countdown_warning: int = -1
var previous_wave_kills: int = 0
var round_stats = RoundStats.new()
var round_report: Label
var report_background: Panel
var report_remaining: float = 0.0
var grenade_event_serial: int = 0
var wave_kills: int = 0
var banner_timer: float = 0.0
var banner_title: String = ""
var banner_subtitle: String = ""
var spawn_remaining: int = 0
var alive: int = 0
var spawn_clock: float = 0.0
var spawn_retry_count: int = 0
var shop_open: bool = false
var shop_id: String = ""
var shop_page: int = 0
var shop_prev_button: Button
var shop_next_button: Button
var shops: Array = []
var status_text: String = ""
var status_timer: float = 0.0
var threat_indicators: Array[Line2D] = []
var hitmarker: Control
var threat_durations: Array[float] = [0.0, 0.0, 0.0, 0.0]
var hud: Label
var kills_hud: Label
var wave_caption_hud: Label
var wave_number_hud: Label
var weapon_name_hud: Label
var ammo_reserve_hud: Label
var ammo_reload_hud: Label
var combat_hud_root: Control
var hud_groups: Dictionary = {}
var ammo_hud: Label
var support_hud: Label
var challenges_hud: Label
var waves_hud: Label
var wave_progress: ProgressBar
var health_bar: ProgressBar
var armor_bar: ProgressBar
var banner_panel: Panel
var banner_heading: Label
var banner_caption: Label
var help_hud: Label
var interaction_panel: Panel
var message_hud: Label
var reward_hud: Label
var reward_timer: float = 0.0
var fps_hud: Label
var shop_panel: Panel
var shop_hud: Label
var shop_title_hud: Label
var shop_wallet_hud: Label
var shop_option_buttons: Array[Button] = []
var shop_tab_buttons: Dictionary = {}
var health_text_hud: Label
var armor_text_hud: Label
var damage_overlay: ColorRect
var death_panel: Panel
var death_hud: Label
const RECORD_PATH := "user://frontline_best_wave.txt"

func _ready() -> void:
    randomize()
    _load_record()
    _create_world()
    player = SurvivalPlayer.new()
    player.position = Vector3(0, 1.7, 0)
    add_child(player)
    player.grenade_requested.connect(_throw_grenade)
    player.player_died.connect(_on_player_died)
    player.headshot_confirmed.connect(_on_headshot)
    player.hit_confirmed.connect(_on_hit_confirmed)
    player.shot_resolved.connect(_on_shot_resolved)
    player.downed_started.connect(_on_player_downed)
    player.downed_recovered.connect(_on_player_recovered)
    player.shot_fired.connect(_on_shot_fired)
    player.damage_received.connect(_on_player_damage)
    _create_ui()
    game_menu = SurvivalGameMenu.new()
    add_child(game_menu)
    game_menu.pause_requested.connect(_prepare_pause)
    game_menu.start_requested.connect(_on_game_start)
    game_menu.resume_requested.connect(_on_resume)
    game_menu.restart_requested.connect(_restart_game)
    game_menu.open_main()
    _notify("CAMPO DE TESTES  |  ONDAS CONTINUAS", 3.0)

func _on_game_start() -> void:
    _show_banner("CAMPO DE TESTES", "25 segundos para comprar equipamentos antes da primeira onda.", 4.0)
    _notify("USE F PERTO DAS ESTACOES PARA COMPRAR  |  $1200 PARA TESTES", 4.0)

func _on_resume() -> void:
    pass

func _prepare_pause() -> void:
    if shop_open:
        _close_shop()

func _restart_game() -> void:
    get_tree().paused = false
    get_tree().reload_current_scene()

func _process(delta: float) -> void:
    if status_timer > 0.0:
        status_timer -= delta
    for i in range(threat_durations.size()):
        threat_durations[i] = maxf(0.0, threat_durations[i] - delta)
    reward_timer = maxf(0.0, reward_timer - delta)
    report_remaining = maxf(0.0, report_remaining - delta)
    banner_timer = maxf(0.0, banner_timer - delta)
    _refresh_ui()

func _physics_process(delta: float) -> void:
    # Physics scene queries for safe spawns must be made in a physics callback.
    if player.dead:
        return
    if phase == "break":
        break_remaining = maxf(0.0, break_remaining - delta)
        if wave > 0:
            var seconds_left := ceili(break_remaining)
            if seconds_left != countdown_warning and seconds_left in [15, 10, 5, 4, 3, 2, 1]:
                countdown_warning = seconds_left
                if seconds_left == 15 or seconds_left == 5:
                    _notify("PROXIMA ONDA EM %d SEGUNDOS!" % seconds_left, 1.6)
        if break_remaining <= 0.0:
            _begin_wave()
    elif phase == "wave":
        round_stats.tick(delta)
        spawn_clock -= delta
        if spawn_remaining > 0 and alive < MAX_ACTIVE_ENEMIES and spawn_clock <= 0.0:
            var spawned := _spawn_enemy()
            spawn_clock = maxf(0.35, 0.95 - float(wave) * 0.025) if spawned else 0.60
        if spawn_remaining <= 0 and alive <= 0:
            _end_wave()

func _unhandled_input(event: InputEvent) -> void:
    if not (event is InputEventKey) or not event.pressed or event.echo:
        return
    if player.dead:
        if event.keycode == KEY_ENTER or event.keycode == KEY_KP_ENTER:
            get_tree().reload_current_scene()
        return
    if event.keycode == KEY_F:
        if shop_open:
            _close_shop()
        else:
            var nearby_loot := _nearest_loot()
            if nearby_loot != null:
                _collect_loot(nearby_loot)
            else:
                var nearby := _nearest_shop()
                if nearby != "":
                    _open_shop(nearby)
    elif shop_open:
        if event.keycode >= KEY_1 and event.keycode <= KEY_5:
            _buy(event.keycode - KEY_1)
        elif event.keycode in [KEY_TAB, KEY_E, KEY_RIGHT]:
            _change_shop_page(1)
        elif event.keycode in [KEY_Q, KEY_LEFT]:
            _change_shop_page(-1)
    elif event.keycode == KEY_3:
        _call_squad()
    elif event.keycode == KEY_4:
        _call_airstrike()
    elif event.keycode == KEY_N and phase == "break" and wave > 0:
        # A proxima onda vem automaticamente; N so adianta a preparacao.
        break_remaining = 0.0
        _begin_wave()

func _create_world() -> void:
    var world_env := WorldEnvironment.new()
    var environment := Environment.new()
    environment.background_mode = Environment.BG_SKY
    var sky := Sky.new()
    var sky_mat := ProceduralSkyMaterial.new()
    sky_mat.sky_top_color = Color(0.26, 0.51, 0.76)
    sky_mat.sky_horizon_color = Color(0.73, 0.82, 0.86)
    sky_mat.ground_bottom_color = Color(0.17, 0.20, 0.19)
    sky.sky_material = sky_mat
    environment.sky = sky
    environment.ambient_light_source = Environment.AMBIENT_SOURCE_SKY
    environment.ambient_light_energy = 0.65
    world_env.environment = environment
    add_child(world_env)
    var sun := DirectionalLight3D.new()
    sun.rotation_degrees = Vector3(-52, -32, 0)
    sun.light_energy = 1.15
    sun.shadow_enabled = true
    add_child(sun)
    var ground := _add_box(Vector3(0, -0.5, 0), Vector3(52, 1, 52), Color(0.83, 0.87, 0.83))
    var floor_mesh := ground.get_child(0) as MeshInstance3D
    var floor_material := floor_mesh.material_override as StandardMaterial3D
    floor_material.albedo_texture = load("res://assets/textures/asphalt.png")
    floor_material.uv1_scale = Vector3(16, 16, 1)
    _add_box(Vector3(0, 2.2, -26), Vector3(52, 4.4, 1), Color(0.33, 0.37, 0.41))
    _add_box(Vector3(0, 2.2, 26), Vector3(52, 4.4, 1), Color(0.34, 0.37, 0.40))
    _add_box(Vector3(-26, 2.2, 0), Vector3(1, 4.4, 52), Color(0.35, 0.39, 0.41))
    _add_box(Vector3(26, 2.2, 0), Vector3(1, 4.4, 52), Color(0.34, 0.37, 0.39))
    # Deposito militar: containers com nervuras, sacos de areia, tambores e iluminacao.
    _add_container(Vector3(-9, 1.20, -6), Vector3(5.2, 2.4, 2.0), Color(0.33, 0.40, 0.33))
    _add_container(Vector3(9, 1.00, 6), Vector3(5.5, 2.0, 2.0), Color(0.47, 0.34, 0.24))
    _add_container(Vector3(-9, 1.10, 8), Vector3(2.2, 2.2, 4.3), Color(0.26, 0.39, 0.42))
    _add_container(Vector3(10, 0.80, -9), Vector3(2.5, 1.6, 4.0), Color(0.32, 0.36, 0.33))
    _add_sandbags(Vector3(-2, 0.0, -13), 4, 2)
    _add_sandbags(Vector3(2, 0.0, 13), 4, 2)
    _add_sandbags(Vector3(-15, 0.0, 1), 3, 2)
    _add_sandbags(Vector3(16, 0.0, -1), 3, 2)
    _add_depot_decor()
    # Areas de compra distantes entre si: e preciso correr riscos para reabastecer.
    _add_shop("weapons", "ARMAS", Vector3(-19, 0, -19), Color(0.83, 0.30, 0.22))
    _add_shop("gear", "EQUIPAMENTOS", Vector3(19, 0, -19), Color(0.24, 0.67, 0.36))
    _add_shop("support", "SUPORTE", Vector3(0, 0, 21), Color(0.22, 0.62, 0.84))

func _add_cylinder(at: Vector3, radius: float, height: float, color: Color, rot: Vector3 = Vector3.ZERO) -> MeshInstance3D:
    var mesh := CylinderMesh.new()
    mesh.top_radius = radius
    mesh.bottom_radius = radius
    mesh.height = height
    var part := MeshInstance3D.new()
    part.mesh = mesh
    part.position = at
    part.rotation = rot
    var mat := StandardMaterial3D.new()
    mat.albedo_color = color
    mat.metallic = 0.22
    mat.roughness = 0.68
    part.material_override = mat
    add_child(part)
    return part

func _add_container(at: Vector3, dimensions: Vector3, color: Color) -> void:
    _add_box(at, dimensions, color)
    var dark := color.darkened(0.22)
    _add_box(at + Vector3(0, dimensions.y * 0.5 + 0.015, 0), Vector3(dimensions.x + 0.08, 0.05, dimensions.z + 0.08), dark, false)
    for i in range(int(dimensions.x / 0.48)):
        var x: float = at.x - dimensions.x * 0.5 + 0.24 + float(i) * 0.48
        _add_box(Vector3(x, at.y, at.z + dimensions.z * 0.5 + 0.025), Vector3(0.038, dimensions.y - 0.12, 0.045), dark, false)
        _add_box(Vector3(x, at.y, at.z - dimensions.z * 0.5 - 0.025), Vector3(0.038, dimensions.y - 0.12, 0.045), dark, false)
    for i in range(int(dimensions.z / 0.48)):
        var z: float = at.z - dimensions.z * 0.5 + 0.24 + float(i) * 0.48
        _add_box(Vector3(at.x + dimensions.x * 0.5 + 0.026, at.y, z), Vector3(0.045, dimensions.y - 0.12, 0.038), dark, false)
    for side in [-1.0, 1.0]:
        var sx: float = side
        _add_box(Vector3(at.x + sx * (dimensions.x * 0.5), at.y, at.z), Vector3(0.08, dimensions.y + 0.05, 0.10), dark, false)

func _add_sandbags(center: Vector3, count: int, levels: int) -> void:
    var color := Color(0.52, 0.48, 0.34)
    for level in range(levels):
        for i in range(count):
            var x := center.x + (float(i) - float(count - 1) * 0.5) * 0.85 + (0.23 if level % 2 == 1 else 0.0)
            var position := Vector3(x, 0.21 + float(level) * 0.34, center.z)
            # Base invisivel simplificada para impedir atravessar a barricada.
            var sandbag := CapsuleMesh.new()
            sandbag.radius = 0.20
            sandbag.height = 0.82
            var item := MeshInstance3D.new()
            item.mesh = sandbag
            item.position = position
            item.rotation.z = PI * 0.5
            var mat := StandardMaterial3D.new()
            mat.albedo_color = color.lightened(randf_range(0.0, 0.12))
            mat.roughness = 1.0
            item.material_override = mat
            add_child(item)
    var hidden_blocker := _add_box(center + Vector3(0, float(levels) * 0.17, 0), Vector3(float(count) * 0.86, float(levels) * 0.34, 0.39), Color(0.50, 0.47, 0.34), true)
    hidden_blocker.visible = false

func _add_barrel(center: Vector3, color: Color) -> void:
    _add_cylinder(center + Vector3(0, 0.53, 0), 0.34, 1.05, color)
    _add_cylinder(center + Vector3(0, 0.83, 0), 0.35, 0.055, color.lightened(0.16))
    _add_cylinder(center + Vector3(0, 0.20, 0), 0.35, 0.055, color.lightened(0.13))
    _add_cylinder(center + Vector3(0, 1.07, 0), 0.34, 0.03, Color(0.13, 0.18, 0.19))

func _add_depot_decor() -> void:
    # Linhas de pista e faixas de seguranca no patio.
    var paint := Color(0.72, 0.68, 0.47)
    for i in range(8):
        _add_box(Vector3(-13 + float(i) * 3.5, 0.02, -16.7), Vector3(1.5, 0.025, 0.11), paint, false)
    _add_box(Vector3(0, 0.015, -2.2), Vector3(0.10, 0.022, 29.0), Color(0.64, 0.64, 0.53), false)
    # Fachadas do complexo no limite do mapa.
    for x in [-18.0, 0.0, 18.0]:
        _add_box(Vector3(x, 2.3, -25.4), Vector3(7.5, 3.7, 0.18), Color(0.21, 0.26, 0.30), false)
        _add_box(Vector3(x, 4.3, -25.0), Vector3(8.0, 0.12, 1.6), Color(0.13, 0.16, 0.18), false)
        _add_box(Vector3(x, 3.7, -25.25), Vector3(6.4, 0.14, 0.20), Color(0.57, 0.51, 0.31), false)
        for j in range(5):
            _add_box(Vector3(x - 2.7 + float(j) * 1.35, 2.2, -25.29), Vector3(0.045, 3.0, 0.04), Color(0.33, 0.40, 0.43), false)
    for where in [Vector3(-18, 0, -8), Vector3(18, 0, 10), Vector3(-5, 0, 18), Vector3(15, 0, -19)]:
        _add_barrel(where, Color(0.31, 0.44, 0.46))
        _add_barrel(where + Vector3(0.83, 0, 0.25), Color(0.43, 0.34, 0.25))
    for x in [-23.0, 23.0]:
        for z in [-23.0, 23.0]:
            _add_cylinder(Vector3(x, 2.3, z), 0.09, 4.6, Color(0.25, 0.28, 0.28))
            _add_box(Vector3(x, 4.6, z), Vector3(0.8, 0.27, 0.55), Color(0.18, 0.21, 0.21), false)
            _add_box(Vector3(x, 4.5, z - 0.24), Vector3(0.58, 0.13, 0.08), Color(0.88, 0.78, 0.44), false)
    var badge := Label3D.new()
    badge.text = "SETOR 07  /  ZONA DE CONFLITO"
    badge.font_size = 72
    badge.pixel_size = 0.009
    badge.position = Vector3(0, 3.45, -25.1)
    badge.modulate = Color(0.98, 0.89, 0.56)
    add_child(badge)

func _add_box(pos: Vector3, dimensions: Vector3, tint: Color, solid: bool = true) -> Node3D:
    var root: Node3D
    if solid:
        var static_body := StaticBody3D.new()
        static_body.collision_layer = 1
        static_body.collision_mask = 0
        root = static_body
    else:
        root = Node3D.new()
    root.position = pos
    add_child(root)
    var model := MeshInstance3D.new()
    var cube := BoxMesh.new()
    cube.size = dimensions
    model.mesh = cube
    var mat := StandardMaterial3D.new()
    mat.albedo_color = tint
    mat.roughness = 0.92
    model.material_override = mat
    root.add_child(model)
    if solid:
        var shape := CollisionShape3D.new()
        var box_shape := BoxShape3D.new()
        box_shape.size = dimensions
        shape.shape = box_shape
        root.add_child(shape)
    return root

func _add_shop(id: String, title: String, at: Vector3, color: Color) -> void:
    shops.append({"id":id,"name":title,"position":at})
    _add_box(at + Vector3(0, 0.35, 0), Vector3(2.6, 0.7, 1.8), color, false)
    _add_box(at + Vector3(0, 1.05, 0), Vector3(2.1, 0.7, 1.0), Color(0.12, 0.16, 0.18), false)
    var label := Label3D.new()
    label.text = title + "\n[F] INTERAGIR"
    label.font_size = 42
    label.pixel_size = 0.007
    label.position = at + Vector3(0, 2.0, 0)
    label.billboard = BaseMaterial3D.BILLBOARD_ENABLED
    label.modulate = Color(0.94, 0.96, 1.0)
    add_child(label)

func _begin_wave() -> void:
    if phase == "wave" or player.dead:
        return
    if shop_open:
        _close_shop()
    wave += 1
    record_wave = maxi(record_wave, wave)
    _save_record()
    phase = "wave"
    report_remaining = 0.0
    wave_kills = 0
    round_stats.begin(wave)
    spawn_remaining = WaveRules.total_enemies(wave)
    alive = 0
    spawn_retry_count = 0
    spawn_clock = 0.3
    if WaveRules.is_armored_wave(wave):
        # No shrill alert; visual warning gives time to prepare for a heavy.
        _show_banner("ONDA %02d - AMEACA BLINDADA" % wave, _loadout_label(wave) + "  |  PREPARE-SE!", 3.2)
        _notify(WaveRules.wave_alert(wave), 3.2)
    else:
        _show_banner("ONDA %02d" % wave, _loadout_label(wave) + "  |  SOBREVIVA!", 3.2)
        _notify("ONDA %d - ELIMINE TODOS OS INIMIGOS!" % wave, 3.2)

func _loadout_label(number: int) -> String:
    if number < 4: return "SOLDADOS COM ESCOPETAS"
    if number < 7: return "SOLDADOS COM SUBMETRALHADORAS"
    if number < 11: return "SMG + ESCOPETAS"
    if number < 16: return "SOLDADOS COM FUZIS"
    return "FUZIS + METRALHADORAS"

func _select_enemy_weapon(number: int) -> String:
    if number < 4: return "shotgun"
    if number < 7: return "smg"
    if number < 11: return "shotgun" if randf() < 0.32 else "smg"
    if number < 16: return "smg" if randf() < 0.20 else "rifle"
    return "lmg" if randf() < 0.35 else "rifle"

func _spawn_enemy() -> bool:
    if phase != "wave" or player.dead or alive >= MAX_ACTIVE_ENEMIES or spawn_remaining <= 0:
        return false
    var spawn_points: Array[Vector3] = [
        Vector3(-22, 1.5, -22), Vector3(0, 1.5, -23), Vector3(22, 1.5, -22),
        Vector3(-23, 1.5, 0), Vector3(23, 1.5, 0),
        Vector3(-22, 1.5, 22), Vector3(0, 1.5, 23), Vector3(22, 1.5, 22)
    ]
    var stations: Array[Vector3] = []
    for station in shops:
        stations.append(station["position"])
    var selected: Dictionary = SpawnSelector.select_position(
        spawn_points,
        stations,
        get_world_3d().direct_space_state,
        player.global_position,
        -player.camera.global_transform.basis.z
    )
    if not selected.get("valid", false):
        spawn_retry_count += 1
        if spawn_retry_count % 10 == 0:
            push_warning("Sem ponto seguro para spawn na onda %d (tentativas %d)." % [wave, spawn_retry_count])
        return false
    spawn_retry_count = 0
    var pick: Vector3 = selected["position"]
    var enemy := SurvivalEnemy.new()
    var kind: String = WaveRules.kind_for_spawn(wave, spawn_remaining, randf())
    enemy.configure(kind, wave, player, _select_enemy_weapon(wave))
    # Prototype only: first ordinary soldier in a wave uses Quaternius.
    # Keep all other enemies and their current assets for a direct comparison.
    # The experimental rig has no validated animations. Keep it in isolated QA,
    # not in the publicly playable Field of Tests.
    enemy.preview_quaternius = ENABLE_EXPERIMENTAL_HUMANOIDS and kind == "soldier" and spawn_remaining == WaveRules.total_enemies(wave)
    enemy.position = pick
    enemy.defeated.connect(_on_enemy_defeated)
    enemy.combat_defeat.connect(_on_enemy_combat_defeat)
    enemy.loot_dropped.connect(_on_enemy_loot_dropped)
    add_child(enemy)
    alive += 1
    spawn_remaining -= 1
    return true

func _on_enemy_loot_dropped(weapon: String, at: Vector3) -> void:
    # Fallen combatants leave their actual gun; some also leave ammunition.
    # Every pickup and body is time-limited and strictly budgeted for 8GB/iGPU.
    _spawn_loot_pickup("weapon", weapon, at, 0)
    if randf() < 0.32:
        _spawn_loot_pickup("ammo", weapon, at + Vector3(0.45, 0.0, 0.22), 16)
    var corpses := get_tree().get_nodes_in_group("fallen_soldiers")
    if corpses.size() > MAX_CORPSES:
        for i in range(corpses.size() - MAX_CORPSES):
            if is_instance_valid(corpses[i]):
                corpses[i].queue_free()

func _spawn_loot_pickup(kind: String, weapon: String, at: Vector3, ammo: int) -> void:
    var drop := WorldPickup.new()
    drop.configure(kind, weapon, ammo)
    drop.position = Vector3(at.x, 0.02, at.z)
    add_child(drop)
    var loot_items := get_tree().get_nodes_in_group("world_loot")
    if loot_items.size() > MAX_LOOT:
        for i in range(loot_items.size() - MAX_LOOT):
            if is_instance_valid(loot_items[i]):
                loot_items[i].queue_free()

func _nearest_loot() -> Node3D:
    var best: Node3D
    var closest := 2.3
    for item in get_tree().get_nodes_in_group("world_loot"):
        if not is_instance_valid(item) or item.is_queued_for_deletion():
            continue
        var distance: float = Vector2(
            player.global_position.x - item.global_position.x,
            player.global_position.z - item.global_position.z
        ).length()
        if distance < closest:
            best = item
            closest = distance
    return best

func _collect_loot(item: Node3D) -> void:
    var id: String = str(item.get("weapon_id"))
    if not SurvivalPlayer.WEAPONS.has(id):
        return
    if str(item.get("pickup_type")) == "ammo":
        # Ammo belongs to the fallen enemy's weapon, not whichever gun the
        # player happens to be holding. Do not silently convert calibers.
        if not player.owned_weapons.has(id):
            _notify("MUNICAO DE %s  |  PEGUE A ARMA PRIMEIRO" % id.to_upper(), 1.8)
            return
        var maximum: int = int(SurvivalPlayer.WEAPONS[id]["reserve"])
        if player.reserves[id] >= maximum:
            _notify("MUNICAO DE %s JA ESTA COMPLETA" % id.to_upper(), 1.5)
            return
        var received: int = mini(int(item.get("amount")), maximum - int(player.reserves[id]))
        player.reserves[id] += received
        _notify("+%d MUNICAO PARA %s" % [received, id.to_upper()], 1.6)
    elif player.owned_weapons.has(id):
        var maximum: int = int(SurvivalPlayer.WEAPONS[id]["reserve"])
        var received: int = mini(int(SurvivalPlayer.WEAPONS[id]["mag"]), maximum - int(player.reserves[id]))
        player.reserves[id] += maxi(0, received)
        player.switch_weapon(id)
        _notify("%s RECUPERADA  |  +%d MUNICAO" % [id.to_upper(), maxi(0, received)], 1.6)
    else:
        player.equip(id)
        _notify("%s RECOLHIDA DO CHAO" % id.to_upper(), 1.8)
    item.queue_free()

func _on_shot_resolved(hit_enemy: bool, was_headshot: bool) -> void:
    if phase == "wave":
        round_stats.shot(hit_enemy, was_headshot)

func _on_enemy_combat_defeat(enemy_id: int, source: String, was_headshot: bool, event_id: int, bounty: int) -> void:
    if phase != "wave":
        return
    var challenge_award: int = round_stats.defeat(
        enemy_id, source, was_headshot, event_id, round_stats.elapsed, bounty
    )
    if challenge_award > 0:
        wallet += challenge_award
        _notify("DESAFIO CONCLUIDO: +$%d" % challenge_award, 2.8)
    if player.downed and source in ["player", "melee", "grenade"]:
        player.recover_downed(false)

func _on_player_downed() -> void:
    if shop_open:
        _close_shop()
    _show_banner("ULTIMA CHANCE", "10 SEGUNDOS! ELIMINE UM INIMIGO COM A PISTOLA.", 2.8)
    _notify("ULTIMA CHANCE: MATE PARA LEVANTAR  |  KIT SALVA AO ESGOTAR", 3.0)

func _on_player_recovered() -> void:
    _show_banner("RECUPERADO", "RETORNE AO COMBATE", 1.6)

func _on_enemy_defeated(bounty: int) -> void:
    alive = maxi(0, alive - 1)
    wallet += bounty
    kills += 1
    wave_kills += 1
    reward_hud.text = "+$%d   ELIMINACAO" % bounty
    reward_timer = 1.05

func _end_wave() -> void:
    if phase != "wave":
        return
    phase = "break"
    break_duration = float(GameSettings.intermission_seconds)
    break_remaining = break_duration
    countdown_warning = -1
    previous_wave_kills = wave_kills
    var bonus := 60 + wave * 20
    wallet += bonus
    player.heal(15.0)
    round_stats.finish(bonus)
    var accuracy_value: float = round_stats.accuracy()
    var accuracy_text := "--" if accuracy_value < 0.0 else "%d%%" % roundi(accuracy_value)
    # One compact, temporary recap; no central modal, no repeated countdown.
    round_report.text = "ONDA %02d CONCLUIDA   +$%d  |  +15 VIDA\n%d ABATES   •   %d HEADSHOTS   •   PRECISAO %s" % [
        wave, bonus, previous_wave_kills, round_stats.headshot_kills, accuracy_text
    ]
    report_remaining = 4.0
    banner_timer = 0.0
    status_timer = 0.0

func _clock(seconds: float) -> String:
    var remaining: int = maxi(0, ceili(seconds))
    return "%02d:%02d" % [remaining / 60, remaining % 60]

func _is_humanoid_preview_enabled() -> bool:
    return ENABLE_EXPERIMENTAL_HUMANOIDS

func _show_banner(heading: String, caption: String, duration: float) -> void:
    banner_title = heading
    banner_subtitle = caption
    banner_timer = duration

func _nearest_shop() -> String:
    var result := ""
    var distance := 3.6
    for station in shops:
        var d: float = player.global_position.distance_to(station["position"] + Vector3.UP)
        if d < distance:
            distance = d
            result = station["id"]
    return result

func _open_shop(id: String) -> void:
    shop_id = id
    shop_page = 0
    shop_open = true
    player.controls_locked = true
    Input.set_mouse_mode(Input.MOUSE_MODE_VISIBLE)
    _render_shop()

func _close_shop() -> void:
    shop_open = false
    shop_id = ""
    player.controls_locked = false
    if not player.dead and (game_menu == null or not game_menu.active):
        Input.set_mouse_mode(Input.MOUSE_MODE_CAPTURED)

func _render_shop() -> void:
    var titles := {"weapons":"ARSENAL DE ARMAS", "gear":"EQUIPAMENTOS", "support":"CENTRAL DE SUPORTE"}
    shop_title_hud.text = titles[shop_id]
    shop_wallet_hud.text = "SALDO   $%d" % wallet
    var options: Array = SHOP_OPTIONS[shop_id]
    for i in range(shop_option_buttons.size()):
        var button: Button = shop_option_buttons[i]
        var real_index: int = shop_page * 5 + i
        button.visible = real_index < options.size()
        if real_index < options.size():
            var entry: Array = options[real_index]
            var item_id: String = str(entry[2])
            var already_owned := (
                item_id in ["smg", "rifle", "shotgun", "lmg"] and player.owned_weapons.has(item_id)
            )
            var already_equipped := (
                item_id in ["red_dot", "holo", "suppressor", "compensator"]
                and player.has_attachment("optic" if item_id in ["red_dot", "holo"] else "muzzle", item_id)
            ) or (item_id.begins_with("perk_") and player.active_perk == item_id.substr(5))
            if already_owned:
                button.text = "%d   %s       EQUIPAR" % [i + 1, entry[0]]
            elif already_equipped:
                button.text = "%d   %s       EQUIPADO" % [i + 1, entry[0]]
            else:
                button.text = "%d   %s       $%d" % [i + 1, entry[0], entry[1]]
            button.disabled = already_equipped or (not already_owned and wallet < int(entry[1]))
    shop_prev_button.disabled = shop_page <= 0
    shop_next_button.disabled = (shop_page + 1) * 5 >= options.size()
    for id in shop_tab_buttons:
        var tab: Button = shop_tab_buttons[id]
        tab.button_pressed = id == shop_id
        tab.disabled = id != shop_id
    shop_hud.text = "PAGINA %d/%d   |  1-5 COMPRAR   |  Q/E NAVEGAR   |  F FECHAR" % [
        shop_page + 1, ceili(float(options.size()) / 5.0)
    ]

func _change_shop_page(direction: int) -> void:
    if not shop_open:
        return
    var options: Array = SHOP_OPTIONS[shop_id]
    var last_page: int = maxi(0, ceili(float(options.size()) / 5.0) - 1)
    shop_page = clampi(shop_page + direction, 0, last_page)
    _render_shop()

func _switch_shop(id: String) -> void:
    if not shop_open or id != shop_id:
        return
    _render_shop()

func _buy(index: int) -> void:
    var options: Array = SHOP_OPTIONS[shop_id]
    var real_index := shop_page * 5 + index
    if real_index >= options.size() or index < 0:
        return
    var item: Array = options[real_index]
    var price: int = item[1]
    var id: String = item[2]
    if id in ["smg", "rifle", "shotgun", "lmg"] and player.owned_weapons.has(id):
        player.equip(id)
        _notify("EQUIPADA: " + str(item[0]), 2.0)
        _render_shop()
        return
    if wallet < price:
        _notify("Dinheiro insuficiente!", 2.0)
        return
    if id in ["red_dot", "holo", "suppressor", "compensator"]:
        var slot := "optic" if id in ["red_dot", "holo"] else "muzzle"
        if player.has_attachment(slot, id):
            _notify("ACESSORIO JA INSTALADO", 1.5)
            return
    if id.begins_with("perk_") and player.active_perk == id.substr(5):
        _notify("ESTE PERK JA ESTA ATIVO", 1.5)
        return
    if id == "self_revive" and player.self_revive_kits >= 1:
        _notify("JA POSSUI UM KIT DE REANIMACAO", 1.5)
        return
    if id == "upgrade" and player.upgrades >= 3:
        _notify("Arma no nivel maximo!", 2.0)
        return
    if id == "turret" and get_tree().get_nodes_in_group("turrets").size() >= 2:
        _notify("Limite de 2 torretas ativas!", 2.0)
        return
    wallet -= price
    if phase == "wave":
        round_stats.spent(price)
    match id:
        "smg", "rifle", "shotgun", "lmg":
            player.equip(id)
        "ammo":
            player.refill_ammo()
        "red_dot", "holo":
            player.install_attachment("optic", id)
        "suppressor", "compensator":
            player.install_attachment("muzzle", id)
        "self_revive":
            player.self_revive_kits += 1
        "perk_quick_reload", "perk_steady", "perk_fast_ads", "perk_mobility", "perk_resistance":
            player.select_perk(id.substr(5))
        "armor":
            player.add_armor(50.0)
        "medkit":
            player.heal(50.0)
        "upgrade":
            player.upgrades += 1
            player.weapon_upgrades[player.weapon_id] = player.upgrades
        "grenades":
            grenades += 2
        "turret":
            var turret := SurvivalTurret.new()
            var forward := -player.camera.global_transform.basis.z
            forward.y = 0
            turret.position = player.global_position + forward.normalized() * 2.3
            turret.position.y = 0.0
            add_child(turret)
            turret.add_to_group("turrets")
        "squad":
            ally_tokens += 1
        "airstrike":
            airstrike_tokens += 1
    _notify("COMPRADO: " + str(item[0]), 2.2)
    _render_shop()

func _call_squad() -> void:
    if ally_tokens <= 0:
        _notify("COMPRE UM ESQUADRAO NA ESTACAO DE SUPORTE", 2.5)
        return
    if get_tree().get_nodes_in_group("allies").size() >= 6:
        _notify("LIMITE DE 6 SOLDADOS ALIADOS ATIVOS", 2.5)
        return
    ally_tokens -= 1
    for side in [-1.0, 1.0]:
        var fighter := SurvivalAlly.new()
        fighter.configure(player)
        fighter.position = player.global_position + player.global_transform.basis.x * (side * 1.8)
        fighter.position.y = 1.3
        add_child(fighter)
    _show_banner("REFORCOS EM CAMPO", "2 SOLDADOS ALIADOS MOBILIZADOS", 2.5)
    _notify("EQUIPE ALIADA ATIVA", 2.5)

func _call_airstrike() -> void:
    if airstrike_tokens <= 0:
        _notify("COMPRE ATAQUE AEREO NA ESTACAO DE SUPORTE", 2.5)
        return
    if phase != "wave":
        _notify("ATAQUE AEREO DISPONIVEL DURANTE O COMBATE", 2.5)
        return
    airstrike_tokens -= 1
    var origin := player.camera.global_position
    var forward := -player.camera.global_transform.basis.z
    var hit_query := PhysicsRayQueryParameters3D.create(origin, origin + forward * 75.0)
    hit_query.exclude = [player.get_rid()]
    hit_query.collision_mask = 3
    var hit := get_world_3d().direct_space_state.intersect_ray(hit_query)
    var target := origin + forward * 32.0
    if not hit.is_empty():
        target = hit["position"]
    target.y = maxf(target.y, 0.10)
    _notify("ATAQUE AEREO SOLICITADO! IMPACTO EM 1 SEGUNDO", 2.5)
    # Marcador temporario no solo. A explosao usa dano em area, nao elimina o mapa inteiro.
    var marker := MeshInstance3D.new()
    var marker_mesh := CylinderMesh.new()
    marker_mesh.top_radius = 1.7
    marker_mesh.bottom_radius = 1.7
    marker_mesh.height = 0.025
    marker.mesh = marker_mesh
    var marker_mat := StandardMaterial3D.new()
    marker_mat.albedo_color = Color(0.55, 0.85, 0.96, 0.60)
    marker_mat.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
    marker_mat.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
    marker.material_override = marker_mat
    marker.position = Vector3(target.x, 0.06, target.z)
    add_child(marker)
    var timer := get_tree().create_timer(1.0)
    timer.timeout.connect(_airstrike_impact.bind(target, marker))

func _airstrike_impact(at: Vector3, marker: MeshInstance3D) -> void:
    if is_instance_valid(marker):
        marker.queue_free()
    if not is_inside_tree():
        return
    var defeated_count := 0
    for enemy in get_tree().get_nodes_in_group("enemies"):
        var victim := enemy as SurvivalEnemy
        if is_instance_valid(victim) and not victim.dead:
            var distance := victim.global_position.distance_to(at)
            if distance < 13.0:
                victim.take_damage(275.0 * (1.0 - distance / 18.0))
                defeated_count += 1
    var blast := MeshInstance3D.new()
    var sphere := SphereMesh.new()
    sphere.radius = 1.0
    sphere.height = 2.0
    blast.mesh = sphere
    var mat := StandardMaterial3D.new()
    mat.albedo_color = Color(1.0, 0.54, 0.18, 0.48)
    mat.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
    mat.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
    blast.material_override = mat
    blast.position = at
    add_child(blast)
    var tween := create_tween()
    tween.tween_property(blast, "scale", Vector3(10.0, 6.0, 10.0), 0.38)
    tween.tween_callback(blast.queue_free)
    _notify("IMPACTO AEREO  |  %d ALVOS ATINGIDOS" % defeated_count, 3.0)

func _throw_grenade() -> void:
    if grenades <= 0:
        _notify("SEM GRANADAS  |  COMPRE NA ESTACAO DE EQUIPAMENTOS", 1.8)
        return
    if player.dead or player.downed or shop_open or player.grenade_throw_timer > 0.0:
        return
    grenades -= 1
    grenade_event_serial += 1
    var grenade: SurvivalFragGrenade = FragGrenade.new()
    grenade.configure(player, -grenade_event_serial)
    var forward := -player.camera.global_transform.basis.z.normalized()
    var right := player.camera.global_transform.basis.x.normalized()
    add_child(grenade)
    grenade.global_position = player.camera.global_position + forward * 0.65 + right * 0.16 - Vector3.UP * 0.12
    grenade.launch(forward)
    grenade.detonated.connect(_on_frag_detonated)
    player.play_grenade_throw()

func _on_frag_detonated(hit_count: int) -> void:
    if hit_count > 0:
        reward_hud.text = "FRAG  |  %d ALVOS ATINGIDOS" % hit_count
        reward_timer = 1.25

func _on_player_died() -> void:
    if shop_open:
        _close_shop()
    if GameSettings.training_respawns:
        # Modo de testes: nao perder ondas, dinheiro ou armas ao ficar sem vida.
        call_deferred("_revive_training_player")
    else:
        game_menu.enabled_pause = false
        _notify("VOCE MORREU. ENTER PARA REINICIAR.", 120.0)

func _revive_training_player() -> void:
    if not is_instance_valid(player):
        return
    player.revive_for_testing()
    _show_banner("REANIMADO", "O progresso foi mantido. Continue a onda %d." % maxi(wave, 1), 2.3)
    _notify("VIDA RESTAURADA  |  5s DE PROTECAO", 3.0)

func _on_hit_confirmed() -> void:
    if GameSettings.hitmarker_enabled and is_instance_valid(hitmarker):
        hitmarker.call("flash", false)

func _on_headshot() -> void:
    if GameSettings.hitmarker_enabled and is_instance_valid(hitmarker):
        hitmarker.call("flash", true)
    wallet += 12
    if phase == "wave":
        round_stats.money_headshots += 12
    reward_hud.text = "+$12  |  TIRO NA CABECA"
    reward_timer = 1.15

func _on_player_damage(source_position: Vector3, _actual_damage: float) -> void:
    if phase == "wave":
        round_stats.take_hit(_actual_damage)
    # 0 frente, 1 direita, 2 tras, 3 esquerda.
    # Projecao apenas horizontal evita indicadores trocados em desniveis.
    var direction := source_position - player.global_position
    direction.y = 0.0
    if direction.length_squared() < 0.01:
        threat_durations[0] = 1.10
        return
    var relative := player.global_transform.basis.inverse() * direction.normalized()
    var angle := atan2(relative.x, -relative.z)
    var index := 0
    if absf(angle) >= PI * 0.75:
        index = 2
    elif angle >= PI * 0.25:
        index = 1
    elif angle <= -PI * 0.25:
        index = 3
    threat_durations[index] = 1.10

func _on_shot_fired(at: Vector3, hit_enemy: bool) -> void:
    # Bullet trails are a very short streak, not a 30-metre luminous beam.
    # Restricting these to occasional rounds also reduces draw calls on iGPU.
    if not is_instance_valid(player):
        return
    if hit_enemy:
        var existing := get_tree().get_nodes_in_group("blood_fx")
        if existing.size() < MAX_BLOOD_EFFECTS:
            var blood := BloodImpact.new()
            blood.position = at
            add_child(blood)
    var from := player.gun.to_global(player.muzzle_flash.position)
    var offset := at - from
    if offset.length() > 0.4 and (player.weapon_id == "shotgun" or randf() < 0.30):
        var direction := offset.normalized()
        var travel := minf(offset.length(), 38.0)
        var streak_length := minf(travel, 1.25)
        var lead := minf(travel * 0.32, 1.8)
        var tracer := MeshInstance3D.new()
        var streak := CylinderMesh.new()
        streak.top_radius = 0.0025
        streak.bottom_radius = 0.005
        streak.height = streak_length
        tracer.mesh = streak
        tracer.position = from + direction * (lead + streak_length * 0.5)
        tracer.quaternion = Quaternion(Vector3.UP, direction)
        var mat := StandardMaterial3D.new()
        mat.albedo_color = Color(1.0, 0.76, 0.49, 0.28)
        mat.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
        mat.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
        tracer.material_override = mat
        add_child(tracer)
        var streak_tween := create_tween().set_parallel(true)
        streak_tween.tween_property(tracer, "scale", Vector3(0.05, 1.0, 0.05), 0.075)
        streak_tween.tween_property(mat, "albedo_color", Color(1.0, 0.76, 0.49, 0.0), 0.075)
        streak_tween.chain().tween_callback(tracer.queue_free)
    # Estojo leve sai pela janela lateral da arma.
    var casing := MeshInstance3D.new()
    var shell_mesh := CylinderMesh.new()
    shell_mesh.top_radius = 0.008
    shell_mesh.bottom_radius = 0.008
    shell_mesh.height = 0.028
    casing.mesh = shell_mesh
    casing.position = player.gun.to_global(Vector3(0.13, 0.01, -0.12))
    var shell_mat := StandardMaterial3D.new()
    shell_mat.albedo_color = Color(0.67, 0.52, 0.23)
    shell_mat.metallic = 0.76
    shell_mat.roughness = 0.36
    casing.material_override = shell_mat
    add_child(casing)
    var drop := create_tween().set_parallel(true)
    drop.tween_property(casing, "position", casing.position + Vector3(randf_range(0.16, 0.44), -0.6, 0.2), 0.34)
    drop.tween_property(casing, "rotation", Vector3(4.0, 2.0, 3.0), 0.34)
    drop.chain().tween_callback(casing.queue_free)
    if player.camera.global_position.distance_to(at) > 55.0:
        return
    var impact := MeshInstance3D.new()
    var mesh := SphereMesh.new()
    mesh.radius = 0.06 if hit_enemy else 0.035
    mesh.height = 0.12 if hit_enemy else 0.07
    impact.mesh = mesh
    impact.position = at
    var impact_mat := StandardMaterial3D.new()
    impact_mat.albedo_color = Color(0.69, 0.18, 0.12, 0.67) if hit_enemy else Color(0.62, 0.60, 0.51, 0.60)
    impact_mat.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
    impact.material_override = impact_mat
    add_child(impact)
    var impact_tween := create_tween()
    impact_tween.set_parallel(true)
    impact_tween.tween_property(impact, "scale", Vector3(1.7, 1.7, 1.7), 0.19)
    impact_tween.tween_property(impact_mat, "albedo_color", Color(impact_mat.albedo_color.r, impact_mat.albedo_color.g, impact_mat.albedo_color.b, 0.0), 0.19)
    impact_tween.chain().tween_callback(impact.queue_free)



func _load_record() -> void:
    if FileAccess.file_exists(RECORD_PATH):
        var file := FileAccess.open(RECORD_PATH, FileAccess.READ)
        if file != null:
            record_wave = maxi(0, int(file.get_as_text().strip_edges()))

func _save_record() -> void:
    var file := FileAccess.open(RECORD_PATH, FileAccess.WRITE)
    if file != null:
        file.store_string(str(record_wave))

func _notify(what: String, duration: float) -> void:
    status_text = what
    status_timer = duration

func _create_ui() -> void:
    var layer := CanvasLayer.new()
    layer.layer = 5
    add_child(layer)
    var root := Control.new()
    root.name = "CombatHUD"
    root.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
    root.mouse_filter = Control.MOUSE_FILTER_IGNORE
    layer.add_child(root)
    combat_hud_root = root

    # The damage vignette follows the viewport instead of assuming 1280x720.
    damage_overlay = ColorRect.new()
    damage_overlay.color = Color(0.65, 0.04, 0.03, 0.0)
    damage_overlay.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
    damage_overlay.mouse_filter = Control.MOUSE_FILTER_IGNORE
    root.add_child(damage_overlay)
    hitmarker = HitMarkerUI.new()
    hitmarker.name = "HitConfirmationOnly"
    hitmarker.anchor_left = 0.5
    hitmarker.anchor_right = 0.5
    hitmarker.anchor_top = 0.5
    hitmarker.anchor_bottom = 0.5
    hitmarker.mouse_filter = Control.MOUSE_FILTER_IGNORE
    root.add_child(hitmarker)

    # Four true edge-anchored typographic regions, not box-shaped modal cards.
    # Light strokes give alignment without putting large black slabs over the map.
    var credit_zone := _hud_group(root, "Credits", Vector2.ZERO, Vector2(27, 22), Vector2(232, 89))
    _hud_rule(credit_zone, Vector2(0, 0), Vector2(0, 79), Color(0.48, 0.88, 0.78, 0.90), 2.0)
    _hud_label(credit_zone, Vector2(12, 0), Vector2(190, 18), 11, Color(0.68, 0.79, 0.79)).text = "CRÉDITOS"
    hud = _hud_label(credit_zone, Vector2(12, 13), Vector2(215, 39), 29)
    kills_hud = _hud_label(credit_zone, Vector2(12, 57), Vector2(210, 23), 14, Color(0.78, 0.87, 0.85))
    _hud_rule(credit_zone, Vector2(12, 52), Vector2(127, 52), Color(0.43, 0.74, 0.70, 0.47), 1.0)

    var wave_zone := _hud_group(root, "Wave", Vector2(0.5, 0.0), Vector2(-191, 19), Vector2(382, 83))
    wave_number_hud = _hud_label(wave_zone, Vector2(8, 12), Vector2(64, 50), 36)
    _hud_rule(wave_zone, Vector2(80, 13), Vector2(80, 57), Color(0.44, 0.83, 0.79, 0.8), 2.0)
    wave_caption_hud = _hud_label(wave_zone, Vector2(94, 9), Vector2(278, 18), 11, Color(0.51, 0.85, 0.76))
    waves_hud = _hud_label(wave_zone, Vector2(94, 27), Vector2(278, 30), 19)
    wave_progress = _make_hud_bar(wave_zone, Vector2(10, 71), Vector2(362, 5), Color(0.42, 0.87, 0.75))
    wave_progress.scale.y = 0.38
    _hud_rule(wave_zone, Vector2(10, 80), Vector2(372, 80), Color(0.67, 0.79, 0.79, 0.35), 1.0)

    var support_zone := _hud_group(root, "Support", Vector2(1.0, 0.0), Vector2(-337, 19), Vector2(311, 82))
    _hud_label(support_zone, Vector2(0, 17), Vector2(174, 19), 11, Color(0.63, 0.80, 0.80)).text = "RECURSOS TÁTICOS"
    fps_hud = _hud_label(support_zone, Vector2(194, 0), Vector2(116, 22), 11, Color(0.78, 0.88, 0.85))
    fps_hud.horizontal_alignment = HORIZONTAL_ALIGNMENT_RIGHT
    support_hud = _hud_label(support_zone, Vector2(0, 40), Vector2(311, 40), 12, Color(0.86, 0.92, 0.88))
    support_hud.horizontal_alignment = HORIZONTAL_ALIGNMENT_RIGHT
    _hud_rule(support_zone, Vector2(130, 35), Vector2(311, 35), Color(0.36, 0.72, 0.72, 0.48), 1.0)

    var life_zone := _hud_group(root, "Vitals", Vector2(0.0, 1.0), Vector2(25, -112), Vector2(245, 91))
    _hud_label(life_zone, Vector2(0, 0), Vector2(128, 20), 11, Color(0.69, 0.81, 0.78)).text = "VIDA"
    health_text_hud = _hud_label(life_zone, Vector2(0, 19), Vector2(79, 52), 34)
    health_bar = _make_hud_bar(life_zone, Vector2(88, 39), Vector2(152, 5), Color(0.44, 0.91, 0.61))
    health_bar.scale.y = 0.42
    armor_text_hud = _hud_label(life_zone, Vector2(88, 51), Vector2(152, 19), 12, Color(0.69, 0.83, 0.92))
    armor_bar = _make_hud_bar(life_zone, Vector2(88, 74), Vector2(152, 4), Color(0.40, 0.68, 0.98))
    armor_bar.scale.y = 0.42
    _hud_rule(life_zone, Vector2(0, 81), Vector2(65, 81), Color(0.44, 0.88, 0.64, 0.62), 2.0)

    var weapon_zone := _hud_group(root, "Weapon", Vector2(1.0, 1.0), Vector2(-276, -113), Vector2(251, 91))
    weapon_name_hud = _hud_label(weapon_zone, Vector2(0, 2), Vector2(248, 24), 14, Color(0.79, 0.87, 0.88))
    weapon_name_hud.horizontal_alignment = HORIZONTAL_ALIGNMENT_RIGHT
    ammo_hud = _hud_label(weapon_zone, Vector2(0, 26), Vector2(166, 53), 36)
    ammo_hud.horizontal_alignment = HORIZONTAL_ALIGNMENT_RIGHT
    ammo_reserve_hud = _hud_label(weapon_zone, Vector2(172, 48), Vector2(76, 28), 18, Color(0.66, 0.79, 0.78))
    ammo_reload_hud = _hud_label(weapon_zone, Vector2(0, 77), Vector2(248, 17), 11, Color(0.96, 0.77, 0.42))
    ammo_reload_hud.horizontal_alignment = HORIZONTAL_ALIGNMENT_RIGHT
    _hud_rule(weapon_zone, Vector2(126, 80), Vector2(248, 80), Color(0.53, 0.84, 0.77, 0.52), 1.0)

    # Full objective details are optional, on TAB while in combat.
    var objective_zone := _hud_group(root, "Objectives", Vector2(0.0, 1.0), Vector2(26, -155), Vector2(570, 32))
    challenges_hud = _hud_label(objective_zone, Vector2(0, 0), Vector2(568, 28), 12, Color(0.81, 0.89, 0.73))

    # Context actions occupy one short strip at the bottom, never mid-screen.
    var interact_zone := _hud_group(root, "Interaction", Vector2(0.5, 1.0), Vector2(-166, -53), Vector2(332, 30))
    interaction_panel = Panel.new()
    interaction_panel.name = "ContextPrompt"
    interaction_panel.position = Vector2.ZERO
    interaction_panel.size = Vector2(332, 30)
    var prompt_style := StyleBoxFlat.new()
    prompt_style.bg_color = Color(0.01, 0.025, 0.033, 0.42)
    prompt_style.border_color = Color(0.43, 0.86, 0.75, 0.56)
    prompt_style.set_border_width_all(0)
    prompt_style.border_width_bottom = 1
    interaction_panel.add_theme_stylebox_override("panel", prompt_style)
    interaction_panel.mouse_filter = Control.MOUSE_FILTER_IGNORE
    interact_zone.add_child(interaction_panel)
    help_hud = _hud_label(interaction_panel, Vector2(7, 5), Vector2(318, 21), 13, Color(0.94, 0.91, 0.78))
    help_hud.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER

    # Event lane: one announcement at a time, rendered as text without a box.
    var event_zone := _hud_group(root, "Events", Vector2(0.5, 0.0), Vector2(-218, 110), Vector2(436, 83))
    report_background = Panel.new()
    report_background.name = "WaveRecapNoBackdrop"
    report_background.size = Vector2(436, 49)
    report_background.add_theme_stylebox_override("panel", StyleBoxEmpty.new())
    report_background.mouse_filter = Control.MOUSE_FILTER_IGNORE
    event_zone.add_child(report_background)
    round_report = _hud_label(report_background, Vector2(0, 0), Vector2(436, 47), 13, Color(0.82, 0.96, 0.86))
    round_report.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
    banner_panel = Panel.new()
    banner_panel.name = "EventCaptionNoBackdrop"
    banner_panel.size = Vector2(436, 45)
    banner_panel.add_theme_stylebox_override("panel", StyleBoxEmpty.new())
    banner_panel.mouse_filter = Control.MOUSE_FILTER_IGNORE
    event_zone.add_child(banner_panel)
    banner_heading = _hud_label(banner_panel, Vector2(0, 0), Vector2(436, 24), 19, Color(0.54, 0.92, 0.81))
    banner_heading.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
    banner_caption = _hud_label(banner_panel, Vector2(0, 25), Vector2(436, 20), 12, Color(0.91, 0.94, 0.91))
    banner_caption.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
    message_hud = _hud_label(event_zone, Vector2(0, 50), Vector2(436, 22), 13, Color(0.97, 0.85, 0.60))
    message_hud.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER

    var reward_zone := _hud_group(root, "Rewards", Vector2(1.0, 0.0), Vector2(-330, 112), Vector2(304, 32))
    reward_hud = _hud_label(reward_zone, Vector2(0, 0), Vector2(304, 29), 14, Color(0.51, 0.96, 0.69))
    reward_hud.horizontal_alignment = HORIZONTAL_ALIGNMENT_RIGHT

    var damage_zone := _hud_group(root, "Direction", Vector2(0.5, 0.5), Vector2.ZERO, Vector2.ZERO)
    # Rounded direction indicators are centered on the viewport dynamically.
    for angle_deg in [-90.0, 0.0, 90.0, 180.0]:
        var arc := Line2D.new()
        arc.width = 5.0
        arc.default_color = Color(0.96, 0.27, 0.19, 0.87)
        var mid: float = deg_to_rad(angle_deg)
        for point_index in range(13):
            var ang: float = mid + deg_to_rad(-20.0 + point_index * (40.0 / 12.0))
            arc.add_point(Vector2(cos(ang) * 151.0, sin(ang) * 151.0))
        arc.visible = false
        damage_zone.add_child(arc)
        threat_indicators.append(arc)
    report_background.visible = false
    banner_panel.visible = false

    # Loja com abas e botoes clicaveis; durante ela o mouse fica visivel.
    shop_panel = Panel.new()
    shop_panel.position = Vector2(335, 132)
    shop_panel.size = Vector2(610, 477)
    _style_panel(shop_panel, Color(0.035, 0.065, 0.085, 0.98), Color(0.20, 0.58, 0.67, 0.75), 12)
    shop_panel.mouse_filter = Control.MOUSE_FILTER_STOP
    root.add_child(shop_panel)
    shop_title_hud = _add_label(shop_panel, Vector2(26, 20), Vector2(390, 44), 28)
    shop_wallet_hud = _add_label(shop_panel, Vector2(412, 26), Vector2(178, 34), 18)
    shop_wallet_hud.horizontal_alignment = HORIZONTAL_ALIGNMENT_RIGHT
    for i in range(3):
        var id: String = ["weapons", "gear", "support"][i]
        var tab := Button.new()
        tab.text = ["ARMAS", "EQUIP.", "SUPORTE"][i]
        tab.position = Vector2(26 + i * 189, 89)
        tab.size = Vector2(177, 39)
        tab.toggle_mode = true
        tab.focus_mode = Control.FOCUS_NONE
        tab.pressed.connect(_switch_shop.bind(id))
        shop_panel.add_child(tab)
        shop_tab_buttons[id] = tab
    for i in range(5):
        var option := Button.new()
        option.position = Vector2(26, 137 + i * 54)
        option.size = Vector2(558, 46)
        option.add_theme_font_size_override("font_size", 19)
        option.focus_mode = Control.FOCUS_NONE
        option.pressed.connect(_buy.bind(i))
        shop_panel.add_child(option)
        shop_option_buttons.append(option)
    shop_hud = _add_label(shop_panel, Vector2(33, 401), Vector2(540, 20), 14)
    shop_prev_button = Button.new()
    shop_prev_button.text = "ANTERIOR"
    shop_prev_button.position = Vector2(26, 429)
    shop_prev_button.size = Vector2(132, 38)
    shop_prev_button.focus_mode = Control.FOCUS_NONE
    shop_prev_button.pressed.connect(_change_shop_page.bind(-1))
    shop_panel.add_child(shop_prev_button)
    shop_next_button = Button.new()
    shop_next_button.text = "PROXIMA"
    shop_next_button.position = Vector2(165, 429)
    shop_next_button.size = Vector2(130, 38)
    shop_next_button.focus_mode = Control.FOCUS_NONE
    shop_next_button.pressed.connect(_change_shop_page.bind(1))
    shop_panel.add_child(shop_next_button)
    var close_button := Button.new()
    close_button.text = "FECHAR LOJA"
    close_button.position = Vector2(350, 429)
    close_button.size = Vector2(235, 39)
    close_button.focus_mode = Control.FOCUS_NONE
    close_button.pressed.connect(_close_shop)
    shop_panel.add_child(close_button)
    death_panel = Panel.new()
    death_panel.position = Vector2(260, 240)
    death_panel.size = Vector2(760, 220)
    _style_panel(death_panel, Color(0.07, 0.07, 0.08, 0.95), Color(0.83, 0.37, 0.31, 0.66), 13)
    death_panel.mouse_filter = Control.MOUSE_FILTER_IGNORE
    root.add_child(death_panel)
    death_hud = _add_label(death_panel, Vector2(20, 28), Vector2(720, 170), 30)
    death_hud.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
    shop_panel.visible = false
    banner_panel.visible = false
    death_panel.visible = false

func _hud_group(parent: Control, id: String, anchors: Vector2, offset: Vector2, dimensions: Vector2) -> Control:
    var group := Control.new()
    group.name = "HUD_" + id
    group.mouse_filter = Control.MOUSE_FILTER_IGNORE
    parent.add_child(group)
    group.anchor_left = anchors.x
    group.anchor_right = anchors.x
    group.anchor_top = anchors.y
    group.anchor_bottom = anchors.y
    group.offset_left = offset.x
    group.offset_top = offset.y
    group.offset_right = offset.x + dimensions.x
    group.offset_bottom = offset.y + dimensions.y
    hud_groups[id] = group
    return group

func _hud_rule(parent: Node, start: Vector2, finish: Vector2, tint: Color, thickness: float) -> Line2D:
    var line := Line2D.new()
    line.name = "HudHairline"
    line.width = thickness
    line.default_color = tint
    line.points = PackedVector2Array([start, finish])
    parent.add_child(line)
    return line

func _hud_label(parent: Node, where: Vector2, dimensions: Vector2,
        font_size: int, tint: Color = Color(0.94, 0.97, 0.94)) -> Label:
    var label := _add_label(parent, where, dimensions, font_size)
    label.autowrap_mode = TextServer.AUTOWRAP_OFF
    label.clip_text = true
    label.add_theme_color_override("font_color", tint)
    label.add_theme_constant_override("outline_size", 2)
    label.add_theme_color_override("font_outline_color", Color(0, 0, 0, 0.86))
    return label

func _style_panel(panel: Panel, background: Color, border: Color, radius: int = 9) -> void:
    var style := StyleBoxFlat.new()
    style.bg_color = background
    style.border_color = border
    style.set_border_width_all(1)
    style.set_corner_radius_all(radius)
    style.shadow_color = Color(0.0, 0.0, 0.0, 0.30)
    style.shadow_size = 6
    panel.add_theme_stylebox_override("panel", style)

func _make_hud_bar(parent: Node, where: Vector2, dimensions: Vector2, tint: Color) -> ProgressBar:
    var bar := ProgressBar.new()
    bar.position = where
    bar.size = dimensions
    bar.min_value = 0.0
    bar.max_value = 100.0
    bar.show_percentage = false
    bar.mouse_filter = Control.MOUSE_FILTER_IGNORE
    var back := StyleBoxFlat.new()
    back.bg_color = Color(0.07, 0.15, 0.19, 0.81)
    back.set_corner_radius_all(1)
    bar.add_theme_stylebox_override("background", back)
    var fill := StyleBoxFlat.new()
    fill.bg_color = tint
    fill.set_corner_radius_all(1)
    bar.add_theme_stylebox_override("fill", fill)
    parent.add_child(bar)
    return bar

func _ui_bg(parent: Node, where: Vector2, dimensions: Vector2, color: Color) -> void:
    var rect := ColorRect.new()
    rect.position = where
    rect.size = dimensions
    rect.color = color
    rect.mouse_filter = Control.MOUSE_FILTER_IGNORE
    parent.add_child(rect)

func _add_label(parent: Node, where: Vector2, dimensions: Vector2, font_size: int) -> Label:
    var label := Label.new()
    label.position = where
    label.size = dimensions
    label.add_theme_font_size_override("font_size", font_size)
    label.add_theme_color_override("font_color", Color(0.93, 0.95, 0.94))
    label.add_theme_color_override("font_shadow_color", Color(0.0, 0.0, 0.0, 0.72))
    label.add_theme_constant_override("shadow_offset_x", 1)
    label.add_theme_constant_override("shadow_offset_y", 1)
    label.mouse_filter = Control.MOUSE_FILTER_IGNORE
    parent.add_child(label)
    return label

func _refresh_ui() -> void:
    # Typography first: large changing values, small quiet labels, zero HUD cards.
    hud.text = "$%d" % wallet
    kills_hud.text = "%d  ABATES" % kills
    health_text_hud.text = str(ceili(player.health))
    health_text_hud.add_theme_color_override(
        "font_color", Color(1.0, 0.52, 0.46) if player.health <= 30.0 else Color(0.91, 0.98, 0.92)
    )
    armor_text_hud.text = "COLETE  %d" % ceili(player.armor)
    health_bar.value = player.health
    armor_bar.value = player.armor
    if phase == "break":
        wave_number_hud.text = "%02d" % (wave + 1)
        wave_caption_hud.text = "PREPARAÇÃO"
        waves_hud.text = "PRÓXIMA  %s" % _clock(break_remaining)
        wave_progress.value = 100.0 * (1.0 - break_remaining / maxf(break_duration, 0.1))
    else:
        wave_number_hud.text = "%02d" % wave
        wave_caption_hud.text = "EM COMBATE"
        waves_hud.text = "%d  ALVOS RESTANTES" % (alive + spawn_remaining)
        var total := mini(5 + wave * 2, 55)
        wave_progress.value = 100.0 * (1.0 - float(alive + spawn_remaining) / float(maxi(total, 1)))
    if player.downed:
        wave_number_hud.text = "!"
        wave_caption_hud.text = "ÚLTIMA CHANCE"
        waves_hud.text = "REANIME  %02ds" % ceili(player.downed_seconds)

    var gun_name: String = SurvivalPlayer.WEAPONS[player.weapon_id]["name"]
    weapon_name_hud.text = gun_name.to_upper()
    ammo_hud.text = str(player.magazines[player.weapon_id])
    ammo_reserve_hud.text = "/ %d" % int(player.reserves[player.weapon_id])
    ammo_reload_hud.text = "RECARREGANDO" if player.reloading else ""
    support_hud.text = "G FRAG %d    3 REF %d    4 AÉREO %d\nKIT %d     PERK %s" % [
        grenades, ally_tokens, airstrike_tokens, player.self_revive_kits,
        player.active_perk.to_upper() if player.active_perk != "" else "—"
    ]
    # Challenge detail is available only while TAB is held. Not always on
    # screen, where long strings used to compete with the wave and support HUD.
    var show_objectives := phase == "wave" and Input.is_key_pressed(KEY_TAB) and not player.downed
    challenges_hud.visible = show_objectives and not shop_open and not player.dead
    if challenges_hud.visible:
        challenges_hud.text = "METAS +$500: %s  /  %s" % [
            round_stats.active_challenges[0], round_stats.active_challenges[1]
        ]
    var shop_near := _nearest_shop() if not player.dead else ""
    var loot_near := _nearest_loot() if not player.dead else null
    if shop_open:
        help_hud.text = ""
    elif loot_near != null:
        help_hud.text = str(loot_near.call("prompt"))
    elif shop_near != "":
        var shop_names := {"weapons":"ARMAS", "gear":"EQUIPAMENTOS", "support":"SUPORTE"}
        help_hud.text = "F  •  %s" % shop_names.get(shop_near, "LOJA")
    else:
        help_hud.text = ""
    interaction_panel.visible = help_hud.text != "" and not player.dead and not shop_open

    # Strict single-message lane: banners > recap > short status.
    banner_panel.visible = banner_timer > 0.0 and not shop_open and not player.dead
    report_background.visible = not banner_panel.visible and report_remaining > 0.0 and phase == "break" and not shop_open and not player.dead
    message_hud.visible = not banner_panel.visible and not report_background.visible and status_timer > 0.0 and not shop_open and not player.dead
    message_hud.text = status_text if message_hud.visible else ""
    if banner_panel.visible:
        banner_heading.text = banner_title
        banner_caption.text = banner_subtitle
        banner_panel.modulate.a = minf(1.0, banner_timer * 2.0)
    if report_background.visible:
        report_background.modulate.a = minf(1.0, report_remaining * 2.0)

    fps_hud.text = "%d FPS" % Engine.get_frames_per_second()
    fps_hud.visible = GameSettings.show_fps
    reward_hud.visible = reward_timer > 0.0 and not shop_open and not player.dead
    if reward_hud.visible:
        reward_hud.modulate.a = minf(1.0, reward_timer * 2.0)
    shop_panel.visible = shop_open and not player.dead
    # The three interactive shop tabs stay available; gameplay HUD is hidden
    # behind the shop so a separate menu never competes with live combat labels.
    for zone_id in ["Credits", "Wave", "Support", "Vitals", "Weapon", "Objectives", "Rewards"]:
        (hud_groups[zone_id] as Control).visible = not shop_open and not player.dead
    for i in range(threat_indicators.size()):
        var opacity := minf(0.88, threat_durations[i] * 1.30)
        threat_indicators[i].modulate.a = opacity
        threat_indicators[i].visible = GameSettings.damage_direction_enabled and opacity > 0.0 and not shop_open and not player.dead
    damage_overlay.color.a = (1.0 - player.health / 100.0) * 0.09 + player.damage_anim * 0.12
    death_panel.visible = player.dead and not GameSettings.training_respawns
    if death_panel.visible:
        death_hud.text = "FIM DE JOGO\nOnda %d  |  %d abates\nENTER para recomecar" % [wave, kills]
