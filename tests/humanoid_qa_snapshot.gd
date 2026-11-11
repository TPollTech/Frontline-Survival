extends SceneTree
## Rendered A/B evidence: a full-body Quaternius enemy in front of the player.
## Runs under xvfb + Godot Compatibility renderer, not --headless.
var failures: Array[String] = []

func _initialize() -> void:
    call_deferred("_capture")

func _capture() -> void:
    var packed: PackedScene = load("res://scenes/main.tscn")
    if packed == null:
        push_error("QA_HUMANOID_SNAPSHOT_FAIL missing game scene")
        quit(1)
        return
    var game: Node3D = packed.instantiate()
    root.add_child(game)
    await physics_frame
    game.game_menu._start()
    game.phase = "break"
    game.break_remaining = 300.0
    # Keep the gun out of the preview so the character silhouette can be
    # evaluated rather than hidden behind the player's viewmodel.
    game.player.gun.visible = false
    game.player.controls_locked = true
    var enemy_script: Script = load("res://scripts/enemy.gd")
    var soldier: CharacterBody3D = enemy_script.new()
    soldier.configure("soldier", 1, game.player, "rifle")
    soldier.preview_quaternius = true
    soldier.position = Vector3(0.0, 1.0, -4.7)
    soldier.rotation.y = PI
    game.add_child(soldier)
    soldier.set_physics_process(false)
    if soldier.humanoid_visual == null or not bool(soldier.humanoid_visual.get("valid")):
        push_error("QA_HUMANOID_SNAPSHOT_FAIL rig not enabled")
        quit(1)
        return
    game.player.camera.rotation = Vector3.ZERO
    for k in range(12):
        await process_frame
    var viewport: Viewport = game.get_viewport()
    var rendered: Image = viewport.get_texture().get_image()
    if rendered.is_empty() or rendered.get_width() < 500:
        push_error("QA_HUMANOID_SNAPSHOT_FAIL empty or tiny image")
        quit(1)
        return
    var file_path := ProjectSettings.globalize_path("res://docs/qa/humanoid_current.png")
    DirAccess.make_dir_recursive_absolute(file_path.get_base_dir())
    var result: Error = rendered.save_png(file_path)
    if result != OK:
        push_error("QA_HUMANOID_SNAPSHOT_FAIL PNG export error %d" % result)
        quit(1)
        return
    print("QA_HUMANOID_SNAPSHOT_PASS %dx%d %s" % [rendered.get_width(), rendered.get_height(), file_path])
    quit(0)
