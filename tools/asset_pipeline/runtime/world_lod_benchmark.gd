extends SceneTree
## Isolated renderer comparison, not a gameplay or GPU timer benchmark.
## The normal WorldLOD tick receives a deterministic simulated 60 Hz delta
## so each pass has the same camera poses and selector update schedule.
const FRAMES := 240
const ROUTE := [
    Vector3(-22, 1.65, -22), Vector3(22, 1.65, -22),
    Vector3(22, 1.65, 22), Vector3(-22, 1.65, 22),
]
const ORDER := ["fixed_lod0", "automatic", "automatic", "fixed_lod0"]

func _initialize() -> void:
    call_deferred("_run")

func fail(msg: String) -> void:
    push_error("WORLD_LOD_BENCH_FAIL " + msg)
    quit(1)

func pose(camera: Camera3D, index: int, steps_per_side: int = 60) -> void:
    var segment := int(index / float(steps_per_side))
    var weight := float(index % steps_per_side) / float(steps_per_side)
    camera.global_position = ROUTE[segment].lerp(ROUTE[(segment + 1) % 4], weight)
    camera.look_at(Vector3(0, 1.3, 0), Vector3.UP)

func reset_registry(registry: Variant) -> void:
    registry.elapsed = 0.2
    for entry in registry.entries:
        entry.selector.current = 0
        for k in range(entry.parts.size()):
            entry.parts[k].mesh = entry.part_levels[k][0]

func triangle_count(registry: Variant) -> int:
    var count: int = 0
    for entry in registry.entries:
        count += int(entry.triangles[entry.selector.current])
    return count

func memory_sample() -> Dictionary:
    var video := Performance.get_monitor(Performance.RENDER_VIDEO_MEM_USED)
    return {"engine_static_bytes": Performance.get_monitor(Performance.MEMORY_STATIC),
        "render_video_memory_bytes": video if video > 0 else null}

# Separate visual evidence pass: no image readback inside the timed benchmark.
func capture_motion(camera: Camera3D, registry: Variant, output: String) -> void:
    const STEPS_PER_SIDE := 110
    const MOTION_STEPS := STEPS_PER_SIDE * 4
    reset_registry(registry)
    if triangle_count(registry) != 49248:
        fail("motion baseline geometry")
        return
    var assemblies: Array = []
    for entry in registry.entries:
        assemblies.append({"path": str(entry.anchor.get_path()), "family": entry.family})
    var frames: Array = []
    for step in range(MOTION_STEPS + 1):
        await process_frame
        pose(camera, step % MOTION_STEPS, STEPS_PER_SIDE)
        registry.tick(0.1, camera)
        await RenderingServer.frame_post_draw
        var image := root.get_texture().get_image()
        var filename := "motion-%04d.png" % step
        if image == null or image.is_empty() or image.save_png(output.path_join(filename)) != OK:
            fail("motion capture " + str(step))
            return
        var levels: Array[int] = []
        for entry in registry.entries:
            levels.append(entry.selector.current)
        var p := camera.global_position
        frames.append({"index": step, "file": filename, "camera_m": [p.x, p.y, p.z], "levels": levels})
    var report := {"kind": "world_lod_motion", "schema_version": 1, "resolution": [1280, 720],
        "simulated_delta_s": 0.1, "visual_reviewed": false, "hardware_validated": false,
        "assemblies": assemblies, "frames": frames}
    var file := FileAccess.open(output.path_join("world-lod-motion.json"), FileAccess.WRITE)
    if file == null:
        fail("motion report could not be written")
        return
    file.store_string(JSON.stringify(report, "  "))
    file.close()
    print("WORLD_LOD_MOTION_PASS ", frames.size())
    quit(0)

func _run() -> void:
    var output := OS.get_environment("FRONTLINE_LOD_DIR")
    if output.is_empty() or DisplayServer.get_name() == "headless":
        fail("real display and output required")
        return
    root.size = Vector2i(1280, 720)
    var game: Variant = (load("res://scenes/main.tscn") as PackedScene).instantiate()
    game.checkpoint_path = "user://qa-lod-benchmark-" + str(OS.get_process_id()) + ".save"
    root.add_child(game)
    game.game_menu._start()
    game.player.controls_locked = true
    game.player.viewmodel_projection.hide()
    game.combat_hud_root.hide()
    var camera: Camera3D = game.player.camera
    camera.make_current()
    # Freeze gameplay for both modes: this is strictly a renderer comparison.
    game.process_mode = Node.PROCESS_MODE_DISABLED
    Engine.max_fps = 0
    DisplayServer.window_set_vsync_mode(DisplayServer.VSYNC_DISABLED)
    await process_frame
    await RenderingServer.frame_post_draw
    if root.get_visible_rect().size != Vector2(1280, 720) or DisplayServer.window_get_vsync_mode() != DisplayServer.VSYNC_DISABLED:
        fail("required viewport or vsync setting unavailable")
        return
    var registry: Variant = game.world_lod
    if registry.entries.size() != 23:
        fail("expected 23 registered assemblies")
        return
    if OS.get_environment("FRONTLINE_LOD_MOTION") == "1":
        await capture_motion(camera, registry, output)
        return
    var runs: Array = []
    for mode in ORDER:
        reset_registry(registry)
        if triangle_count(registry) != 49248:
            fail("fixed baseline geometry")
            return
        var frame_ms: Array[float] = []
        var triangles: Array[int] = []
        var previous: int = 0
        var start_memory: Dictionary = {}
        for step in range(FRAMES * 2):
            await process_frame
            pose(camera, step % FRAMES)
            if mode == "automatic":
                registry.tick(1.0 / 60.0, camera)
            await RenderingServer.frame_post_draw
            var now := Time.get_ticks_usec()
            if step == FRAMES - 1:
                start_memory = memory_sample()
                # Exclude the memory query from the first measured interval.
                now = Time.get_ticks_usec()
            if step >= FRAMES:
                frame_ms.append(float(now - previous) / 1000.0)
                triangles.append(triangle_count(registry))
            previous = now
        runs.append({"mode": mode, "frame_ms": frame_ms, "registered_triangles": triangles,
            "memory_after_warmup": start_memory, "memory_after_pass": memory_sample()})
    var report := {"kind": "world_lod_benchmark", "schema_version": 1,
        "scope": "frozen_map_camera_route", "resolution": [1280, 720],
        "warmup_frames": FRAMES, "assemblies": 23, "hardware_validated": false,
        "vsync_disabled": true, "cpu": OS.get_processor_name(),
        "gpu": RenderingServer.get_video_adapter_name(), "os": OS.get_name(),
        "godot_version": str(Engine.get_version_info().get("string", "")),
        "system_memory_bytes": OS.get_memory_info().get("physical", 0), "runs": runs}
    var file := FileAccess.open(output.path_join("world-lod-benchmark.json"), FileAccess.WRITE)
    if file == null:
        fail("report could not be written")
        return
    file.store_string(JSON.stringify(report, "  "))
    file.close()
    print("WORLD_LOD_BENCH_PASS 960 measured intervals")
    quit(0)
