extends Node
## Configuracoes persistentes e controle central do audio.

signal changed

const SETTINGS_PATH := "user://frontline_settings.cfg"

var master_volume: float = 48.0
var sfx_volume: float = 28.0
var ui_volume: float = 42.0
var mouse_sensitivity: float = 1.0
var field_of_view: float = 76.0
var fullscreen: bool = false
var show_fps: bool = true
var intermission_seconds: int = 30
var training_respawns: bool = true
var render_scale: float = 1.0
var vsync: bool = true
var invert_mouse_y: bool = false
var hitmarker_enabled: bool = true
var damage_direction_enabled: bool = true

func _ready() -> void:
    _ensure_bus("SFX")
    _ensure_bus("UI")
    _load()
    apply()

func _ensure_bus(name: String) -> void:
    if AudioServer.get_bus_index(name) < 0:
        AudioServer.add_bus()
        var index := AudioServer.bus_count - 1
        AudioServer.set_bus_name(index, name)
        AudioServer.set_bus_send(index, "Master")

func _load() -> void:
    var cfg := ConfigFile.new()
    if cfg.load(SETTINGS_PATH) != OK:
        return
    master_volume = clampf(float(cfg.get_value("audio", "master", master_volume)), 0.0, 100.0)
    sfx_volume = clampf(float(cfg.get_value("audio", "sfx", sfx_volume)), 0.0, 100.0)
    ui_volume = clampf(float(cfg.get_value("audio", "ui", ui_volume)), 0.0, 100.0)
    mouse_sensitivity = clampf(float(cfg.get_value("controls", "mouse_sensitivity", mouse_sensitivity)), 0.35, 3.0)
    field_of_view = clampf(float(cfg.get_value("controls", "fov", field_of_view)), 60.0, 100.0)
    fullscreen = bool(cfg.get_value("video", "fullscreen", fullscreen))
    show_fps = bool(cfg.get_value("video", "fps", show_fps))
    intermission_seconds = clampi(int(cfg.get_value("gameplay", "intermission_seconds", intermission_seconds)), 30, 120)
    training_respawns = bool(cfg.get_value("gameplay", "training_respawns", training_respawns))
    render_scale = clampf(float(cfg.get_value("video", "render_scale", render_scale)), 0.7, 1.0)
    vsync = bool(cfg.get_value("video", "vsync", vsync))
    invert_mouse_y = bool(cfg.get_value("controls", "invert_y", invert_mouse_y))
    hitmarker_enabled = bool(cfg.get_value("gameplay", "hitmarker", hitmarker_enabled))
    damage_direction_enabled = bool(cfg.get_value("gameplay", "damage_direction", damage_direction_enabled))

func _save() -> void:
    var cfg := ConfigFile.new()
    cfg.set_value("audio", "master", master_volume)
    cfg.set_value("audio", "sfx", sfx_volume)
    cfg.set_value("audio", "ui", ui_volume)
    cfg.set_value("controls", "mouse_sensitivity", mouse_sensitivity)
    cfg.set_value("controls", "fov", field_of_view)
    cfg.set_value("video", "fullscreen", fullscreen)
    cfg.set_value("video", "fps", show_fps)
    cfg.set_value("gameplay", "intermission_seconds", intermission_seconds)
    cfg.set_value("gameplay", "training_respawns", training_respawns)
    cfg.set_value("video", "render_scale", render_scale)
    cfg.set_value("video", "vsync", vsync)
    cfg.set_value("controls", "invert_y", invert_mouse_y)
    cfg.set_value("gameplay", "hitmarker", hitmarker_enabled)
    cfg.set_value("gameplay", "damage_direction", damage_direction_enabled)
    var error := cfg.save(SETTINGS_PATH)
    if error != OK:
        push_warning("Nao foi possivel gravar as configuracoes (%d)." % error)

func apply() -> void:
    _set_bus("Master", master_volume)
    _set_bus("SFX", sfx_volume)
    _set_bus("UI", ui_volume)
    var desired_mode := DisplayServer.WINDOW_MODE_FULLSCREEN if fullscreen else DisplayServer.WINDOW_MODE_WINDOWED
    if DisplayServer.window_get_mode() != desired_mode:
        DisplayServer.window_set_mode(desired_mode)
    get_viewport().scaling_3d_scale = render_scale
    if DisplayServer.get_name() != "headless":
        DisplayServer.window_set_vsync_mode(
            DisplayServer.VSYNC_ENABLED if vsync else DisplayServer.VSYNC_DISABLED
        )
    changed.emit()

func _set_bus(bus_name: String, value: float) -> void:
    var index := AudioServer.get_bus_index(bus_name)
    if index < 0:
        return
    AudioServer.set_bus_mute(index, value <= 0.0)
    AudioServer.set_bus_volume_db(index, linear_to_db(maxf(value / 100.0, 0.001)))

func set_value(key: String, value: Variant) -> void:
    match key:
        "master": master_volume = clampf(float(value), 0.0, 100.0)
        "sfx": sfx_volume = clampf(float(value), 0.0, 100.0)
        "ui": ui_volume = clampf(float(value), 0.0, 100.0)
        "sensitivity": mouse_sensitivity = clampf(float(value), 0.35, 3.0)
        "fov": field_of_view = clampf(float(value), 60.0, 100.0)
        "fullscreen": fullscreen = bool(value)
        "fps": show_fps = bool(value)
        "intermission": intermission_seconds = clampi(int(value), 30, 120)
        "training_respawns": training_respawns = bool(value)
        "render_scale": render_scale = clampf(float(value), 0.7, 1.0)
        "vsync": vsync = bool(value)
        "invert_y": invert_mouse_y = bool(value)
        "hitmarker": hitmarker_enabled = bool(value)
        "damage_direction": damage_direction_enabled = bool(value)
        _: return
    apply()
    _save()
