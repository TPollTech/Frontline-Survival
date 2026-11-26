extends SceneTree
## 02-02 evidence: the eight production weapons rendered by the real game
## viewmodel in rest, ADS and mid-reload, captured from the live OpenGL
## viewport. One row per weapon, three columns (repouso, ADS, recarga).
## Real OpenGL capture, not a Windows playtest approval and not a Studio preview.
const GUNS: Array[String] = ["pistol", "smg", "rifle", "shotgun", "lmg", "sniper", "bolt_sniper", "sentinela"]
const POSES: Array[String] = ["rest", "ads", "reload"]
const CELL_W: int = 640
const CELL_H: int = 360

func _initialize() -> void:
	call_deferred("_capture")

func _fail(reason: String) -> void:
	push_error("QA_ARSENAL_VIEWMODEL_FAIL " + reason)
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
	var sheet: Image = Image.create(CELL_W * POSES.size(), CELL_H * GUNS.size(), false, Image.FORMAT_RGBA8)
	sheet.fill(Color(0.025, 0.025, 0.03, 1.0))
	var report: Array[Dictionary] = []
	for row in range(GUNS.size()):
		var id: String = GUNS[row]
		if not specs.has(id):
			_fail("missing weapon spec " + id)
			return
		for col in range(POSES.size()):
			var pose: String = POSES[col]
			game.player.equip(id)
			game.player.pending_weapon_id = ""
			game.player.weapon_attachments.erase(id)
			game.player.reloading = false
			game.player.reload_elapsed = 0.0
			game.player.holster_timer = 0.0
			game.player.equip_anim_timer = 0.0
			game.player.shot_anim = 0.0
			game.player.bolt_cycle_remaining = 0.0
			game.player.melee_anim_timer = 0.0
			game.player.grenade_throw_timer = 0.0
			game.player.sprint_blend = 0.0
			game.player.weapon_wall_blend = 0.0
			game.player.idle_clock = 0.0
			game.player.walk_anim_blend = 0.0
			game.player.muzzle_flash.visible = false
			var ads: bool = pose == "ads"
			if pose == "reload":
				game.player.reloading = true
				game.player.reload_elapsed = float(specs[id]["reload"]) * 0.45
			game.player.aim = ads
			game.player.camera.fov = base_fov * (game.player._ads_fov_multiplier() if ads else 1.0)
			game.player._update_viewmodel_projection(1.0, false, 22.0)
			game.player.gun.position = game.player.get_viewmodel_rest_pose(ads)
			game.player.gun.rotation = Vector3.ZERO
			game.player._animate_viewmodel(0.25, 0.0)
			if is_instance_valid(game.player.optic_reticle):
				game.player.optic_reticle.visible = ads
			for frame in range(5):
				await process_frame
			var rendered: Image = root.get_texture().get_image()
			if rendered.is_empty() or rendered.get_width() < 1000:
				_fail("empty render for %s/%s" % [id, pose])
				return
			report.append({
				"weapon": id, "pose": pose,
				"gun_position": [game.player.gun.position.x, game.player.gun.position.y, game.player.gun.position.z],
				"fov": game.player.camera.fov,
			})
			rendered.resize(CELL_W, CELL_H, Image.INTERPOLATE_BILINEAR)
			sheet.blit_rect(rendered, Rect2i(0, 0, CELL_W, CELL_H),
				Vector2i(col * CELL_W, row * CELL_H))
	var file_path: String = ProjectSettings.globalize_path("res://docs/qa/02-02/godot-arsenal.png")
	DirAccess.make_dir_recursive_absolute(file_path.get_base_dir())
	if sheet.save_png(file_path) != OK:
		_fail("could not save contact sheet")
		return
	var report_path: String = ProjectSettings.globalize_path("res://docs/qa/02-02/godot-arsenal.json")
	var handle := FileAccess.open(report_path, FileAccess.WRITE)
	if handle != null:
		handle.store_string(JSON.stringify({"renderer": RenderingServer.get_video_adapter_name(),
			"driver": RenderingServer.get_current_rendering_driver_name(), "cells": report}, "  "))
		handle.close()
	print("QA_ARSENAL_VIEWMODEL_PASS %dx%d %d poses" % [sheet.get_width(), sheet.get_height(), report.size()])
	quit(0)
