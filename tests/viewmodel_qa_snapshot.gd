extends SceneTree
## Rendered reference: original nine poses plus three real MRS-7 sight configurations.
## Nine cells in row-major order (see docs/qa/viewmodel_layout.md).
## This is a real OpenGL screenshot, not evidence of Windows playtest approval.
const GUNS: Array[String] = ["pistol", "smg", "rifle", "shotgun", "lmg", "rifle", "rifle", "shotgun", "pistol", "sniper", "sniper", "sniper"]
const CELL_W: int = 640
const CELL_H: int = 360

func _initialize() -> void:
    call_deferred("_capture")

func _fail(reason: String) -> void:
    push_error("QA_VIEWMODEL_SNAPSHOT_FAIL " + reason)
    quit(1)

func _capture() -> void:
    var packed: PackedScene = load("res://scenes/main.tscn")
    if packed == null:
        _fail("game scene missing")
        return
    var game: Variant = packed.instantiate()
    root.add_child(game)
    await physics_frame
    game.game_menu._start()
    game.phase = "break"
    game.break_remaining = 300.0
    game.player.controls_locked = true
    game.player.set_physics_process(false)
    game.player.camera.rotation = Vector3.ZERO
    game.player.gun.visible = true
    game.combat_hud_root.visible = false
    var base_fov: float = game.player.camera.fov
    var specs: Dictionary = game.player.get_script().get_script_constant_map().get("WEAPONS", {})
    if not specs.has("rifle") or not specs.has("shotgun"):
        _fail("missing reload configurations")
        return
    var sheet: Image = Image.create(CELL_W * 3, CELL_H * 4, false, Image.FORMAT_RGBA8)
    sheet.fill(Color(0.025, 0.025, 0.03, 1.0))
    for idx in range(GUNS.size()):
        var id: String = GUNS[idx]
        game.player.equip(id)
        if idx == 10:
            game.player.install_attachment("optic", "scope_2x")
        elif idx == 11:
            game.player.install_attachment("optic", "scope_4x")
        game.player.pending_weapon_id = ""
        game.player.reloading = false
        game.player.reload_elapsed = 0.0
        game.player.holster_timer = 0.0
        game.player.equip_anim_timer = 0.0
        game.player.shot_anim = 0.0
        game.player.melee_anim_timer = 0.0
        game.player.grenade_throw_timer = 0.0
        game.player.sprint_blend = 0.0
        game.player.weapon_wall_blend = 0.0
        game.player.idle_clock = 0.0
        game.player.walk_anim_blend = 0.0
        var ads: bool = idx in [5, 9, 10, 11]
        if idx == 6 or idx == 7:
            game.player.reloading = true
            game.player.reload_elapsed = float(specs[id]["reload"]) * (0.45 if idx == 6 else 0.70)
        if idx == 8:
            game.player.shot_anim = 1.0
        game.player.muzzle_flash.visible = idx == 8
        game.player.aim = ads
        game.player.camera.fov = base_fov * (game.player._ads_fov_multiplier() if ads else 1.0)
        var sight: float = 0.252 if id == "sniper" and game.player._sniper_scope() != "" else (0.182 if id == "sniper" else 0.177)
        game.player.gun.position = (
            Vector3(0.0, -game.player.viewmodel_scale * sight, -0.62)
            if ads else Vector3(0.34, -0.27, -0.63)
        )
        game.player.gun.rotation = Vector3.ZERO
        game.player._animate_viewmodel(0.25, 0.0)
        if is_instance_valid(game.player.optic_reticle):
            game.player.optic_reticle.visible = ads
        for frame in range(5):
            await process_frame
        var rendered: Image = game.get_viewport().get_texture().get_image()
        if rendered.is_empty() or rendered.get_width() < 1000:
            _fail("empty render for " + id)
            return
        rendered.resize(CELL_W, CELL_H, Image.INTERPOLATE_BILINEAR)
        sheet.blit_rect(rendered, Rect2i(0, 0, CELL_W, CELL_H),
            Vector2i((idx % 3) * CELL_W, (idx / 3) * CELL_H))
    var file_path: String = ProjectSettings.globalize_path("res://docs/qa/viewmodel_current.png")
    DirAccess.make_dir_recursive_absolute(file_path.get_base_dir())
    if sheet.save_png(file_path) != OK:
        _fail("could not save contact sheet")
        return
    print("QA_VIEWMODEL_SNAPSHOT_PASS %dx%d twelve poses: nine original poses plus MRS-7 iron sight, 2x and 4x" % [
        sheet.get_width(), sheet.get_height()
    ])
    quit(0)
