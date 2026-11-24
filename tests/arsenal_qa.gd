extends SceneTree
## Individual runtime regression using the actual player and an isolated
## in-game collision target. Never loads or changes a real saved game.
const PlayerScript = preload("res://scripts/player.gd")
const IDS: Array[String] = ["pistol", "smg", "rifle", "shotgun", "lmg", "sentinela", "sniper", "bolt_sniper"]

class QATarget extends StaticBody3D:
    var hits: int = 0
    var total: float = 0.0
    func take_damage(amount: float) -> void:
        hits += 1
        total += amount

var failures: Array[String] = []
var results: Array[Dictionary] = []
var checks: int = 0
var resolved_count: int = 0
var fired_count: int = 0

func _initialize() -> void:
    call_deferred("_run")

func _expect(ok: bool, id: String, label: String) -> void:
    checks += 1
    if not ok:
        var message := id + ": " + label
        failures.append(message)
        push_error("ARSENAL_QA_ERROR: " + message)

func _ready_to_fire(player: Variant) -> void:
    player.fire_timer = 0.0
    player.equip_anim_timer = 0.0
    player.grenade_throw_timer = 0.0
    player.melee_timer = 0.0
    player.sprint_blend = 0.0
    player.suppress_fire_until_release = false
    player.camera.rotation = Vector3.ZERO

func _run() -> void:
    var player: Variant = PlayerScript.new()
    root.add_child(player)
    player.set_physics_process(false)
    player.controls_locked = false
    player.shot_fired.connect(func(_at: Vector3, _hit: bool): fired_count += 1)
    player.shot_resolved.connect(func(_hit: bool, _head: bool): resolved_count += 1)
    var target := QATarget.new()
    target.collision_layer = 1
    var collision := CollisionShape3D.new()
    var shape := BoxShape3D.new()
    shape.size = Vector3(4.0, 4.0, 0.5)
    collision.shape = shape
    target.add_child(collision)
    root.add_child(target)
    target.global_position = player.camera.to_global(Vector3(0, 0, -4))
    await physics_frame
    await physics_frame
    var specs: Dictionary = PlayerScript.WEAPONS
    _expect(specs.size() == IDS.size(), "arsenal", "weapon registry coverage")
    for id in IDS:
        var initial_failures: int = failures.size()
        var initial_checks: int = checks
        var spec: Dictionary = specs[id]
        var capacity: int = int(spec["mag"])
        var reserve: int = int(spec["reserve"])
        player.equip(id)
        player.refill_ammo()
        player.aim = false
        player.active_perk = ""
        player.upgrades = 0
        player.shot_spread_kick = 0.0
        _ready_to_fire(player)
        _expect(player.weapon_id == id and player.owned_weapons.has(id), id, "equip")
        _expect(is_instance_valid(player.weapon_model) and is_instance_valid(player.hand_rig), id, "imported body and hand rig")
        _expect(is_instance_valid(player.action_part), id, "moving action mesh")
        _expect(is_instance_valid(player.magazine_part) or id == "shotgun", id, "magazine mesh or integral tube")
        _expect(player.shot_sound.stream is AudioStreamWAV and player.reload_sound.stream is AudioStreamWAV, id, "recorded WAV resources")
        _expect(player.shot_sound.stream.get_length() > 0.0 and player.reload_sound.stream.get_length() > 0.0, id, "nonempty WAV resources")
        _expect(player.magazines[id] == capacity and player.reserves[id] == reserve, id, "initial ammunition")
        var old_serial: int = player.shot_serial
        var old_fired: int = fired_count
        var old_resolved: int = resolved_count
        target.hits = 0
        target.total = 0.0
        player.shoot(Input.MOUSE_MODE_CAPTURED)
        _expect(player.magazines[id] == capacity - 1 and player.reserves[id] == reserve, id, "one round consumed")
        _expect(player.shot_serial == old_serial + 1 and fired_count == old_fired + 1 and resolved_count == old_resolved + 1, id, "single shot signals")
        _expect(target.hits == int(spec["pellets"]) and is_equal_approx(target.total, float(spec["damage"]) * int(spec["pellets"])), id, "real collision target receives expected game damage")
        _expect(is_equal_approx(player.fire_timer, float(spec["rate"])), id, "cooldown configured")
        _expect(player.shot_anim > 0.0 and player.muzzle_flash.visible, id, "visual firing feedback")
        player.shoot(Input.MOUSE_MODE_CAPTURED)
        _expect(player.shot_serial == old_serial + 1 and player.magazines[id] == capacity - 1, id, "cooldown blocks repeated shot")
        _ready_to_fire(player)
        if id == "bolt_sniper":
            player.shoot(Input.MOUSE_MODE_CAPTURED)
            _expect(player.shot_serial == old_serial + 1 and player.bolt_cycle_remaining > 0.0, id, "mechanical cycle blocks shot")
            player._advance_bolt_cycle(player.bolt_cycle_remaining + 0.01)
        player.shoot(Input.MOUSE_MODE_CAPTURED)
        _expect(player.shot_serial == old_serial + 2 and player.magazines[id] == capacity - 2, id, "next permitted shot")
        # Reload transfers exactly the missing ammunition and cannot duplicate it.
        player.start_reload()
        _expect(player.reloading and is_equal_approx(player.reload_timer, float(spec["reload"])), id, "manual reload duration")
        _ready_to_fire(player)
        player.shoot(Input.MOUSE_MODE_CAPTURED)
        _expect(player.shot_serial == old_serial + 2, id, "reload blocks firing")
        player._finish_reload()
        _expect(player.magazines[id] == capacity and player.reserves[id] == reserve - 2, id, "full reload conserves ammunition")
        player._finish_reload()
        _expect(player.magazines[id] == capacity and player.reserves[id] == reserve - 2, id, "late callback cannot duplicate ammunition")
        player.start_reload()
        _expect(not player.reloading, id, "full magazine blocks reload")
        player.magazines[id] = 0
        player.reserves[id] = 2
        player.start_reload()
        player._finish_reload()
        _expect(player.magazines[id] == 2 and player.reserves[id] == 0, id, "partial reserve reload")
        player.start_reload()
        _expect(not player.reloading, id, "empty reserve blocks reload")
        player.magazines[id] = 0
        _ready_to_fire(player)
        player.shoot(Input.MOUSE_MODE_CAPTURED)
        _expect(player.shot_serial == old_serial + 2 and not player.reloading, id, "empty weapon cannot fire")
        player.magazines[id] = 1
        player.reserves[id] = 3
        _ready_to_fire(player)
        player.shoot(Input.MOUSE_MODE_CAPTURED)
        _expect(player.magazines[id] == 0 and player.reloading, id, "last round starts automatic reload")
        player._finish_reload()
        _expect(player.magazines[id] == 3 and player.reserves[id] == 0, id, "automatic reload conserves reserve")
        # Attachment ownership and the two staged precision optics.
        var first_optic: String = "scope_2x" if id in ["sniper", "bolt_sniper"] else "red_dot"
        _expect(player.install_attachment("optic", first_optic), id, "supported optic installs")
        _expect(is_instance_valid(player.optic_reticle), id, "actual optic mesh")
        var next_optic: String = "scope_4x" if id in ["sniper", "bolt_sniper"] else "holo"
        _expect(player.install_attachment("optic", next_optic), id, "alternate or upgraded optic installs")
        _expect(player.install_attachment("muzzle", "suppressor"), id, "suppressor installs")
        _expect(player.install_attachment("muzzle", "compensator"), id, "compensator installs")
        player.equip("smg" if id == "pistol" else "pistol")
        player.equip(id)
        _expect(player.has_attachment("optic", next_optic) and player.has_attachment("muzzle", "compensator"), id, "attachments survive switch")
        _expect(player.magazines[id] == 3 and player.reserves[id] == 0, id, "ammunition survives switch")
        # Isolate each case from the temporary purchases in earlier cases.
        player.weapon_attachments[id] = {"optic": "", "muzzle": ""}
        player._update_gun_mesh()
        player._update_shot_audio()
        var row := {"weapon": id, "checks": checks - initial_checks,
            "status": "pass" if failures.size() == initial_failures else "fail"}
        results.append(row)
        print("QA_ARSENAL_WEAPON " + JSON.stringify(row))
    var report := {"checked": checks, "weapons": results, "failures": failures}
    var output := FileAccess.open("res://docs/qa/arsenal_report.json", FileAccess.WRITE)
    if output == null:
        _expect(false, "arsenal", "could not save report")
    else:
        output.store_string(JSON.stringify(report, "\t"))
        output.close()
    print("QA_ARSENAL_PASS" if failures.is_empty() else "QA_ARSENAL_FAIL")
    quit(0 if failures.is_empty() else 1)
