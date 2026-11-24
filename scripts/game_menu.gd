extends CanvasLayer
class_name SurvivalGameMenu
## Tela inicial, pausa e menu de configuracoes. Funciona com a arvore pausada.

signal load_requested
signal start_requested
signal pause_requested
signal resume_requested
signal restart_requested

var checkpoint_wave := -1
var current_wave := 0
var balance := 0
var pending_action := ""
var kicker: Label
var footer: Label
var rail: MarginContainer
var backdrop: ColorRect
var container: PanelContainer
var title: Label
var subtitle: Label
var navigation: VBoxContainer
var options: VBoxContainer
var options_scroll: ScrollContainer
var settings_tabs: HBoxContainer
var settings_category: String = "graphics"
var mode: String = "main"
var in_options: bool = false
var active: bool = false
var enabled_pause: bool = true

func _ready() -> void:
    process_mode = Node.PROCESS_MODE_ALWAYS
    layer = 20
    _build()
    visible = false

func _input(event: InputEvent) -> void:
    if not (event is InputEventKey) or not event.pressed or event.echo:
        return
    if event.keycode != KEY_ESCAPE:
        return
    if active:
        if pending_action != "":
            _cancel_action()
        elif in_options:
            in_options = false
            _render()
        elif mode == "pause":
            resume()
    elif enabled_pause:
        pause_requested.emit()
        open_pause()
    get_viewport().set_input_as_handled()

func _build() -> void:
    backdrop = ColorRect.new()
    backdrop.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
    backdrop.color = Color(0.018, 0.035, 0.045, 0.91)
    backdrop.mouse_filter = Control.MOUSE_FILTER_STOP
    add_child(backdrop)
    var shade := TextureRect.new()
    var ramp := Gradient.new()
    ramp.colors = PackedColorArray([Color(0.025,0.035,0.032,0.99), Color(0.04,0.05,0.04,0.82), Color(0.07,0.08,0.05,0.1)])
    ramp.offsets = PackedFloat32Array([0.0, 0.44, 1.0])
    var texture := GradientTexture2D.new()
    texture.gradient = ramp
    texture.fill_to = Vector2.RIGHT
    shade.texture = texture
    shade.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
    shade.mouse_filter = Control.MOUSE_FILTER_IGNORE
    backdrop.add_child(shade)
    rail = MarginContainer.new()
    rail.set_anchors_and_offsets_preset(Control.PRESET_CENTER_LEFT)
    rail.grow_vertical = Control.GROW_DIRECTION_BOTH
    rail.offset_left = 64
    backdrop.add_child(rail)
    container = PanelContainer.new()
    container.add_theme_stylebox_override("panel", StyleBoxEmpty.new())
    rail.add_child(container)
    var column := VBoxContainer.new()
    column.add_theme_constant_override("separation", 10)
    container.add_child(column)
    kicker = Label.new()
    kicker.text = "FRONTLINE   /   SURVIVAL 0.9.19"
    kicker.add_theme_font_size_override("font_size", 15)
    kicker.add_theme_color_override("font_color", Color(0.84, 0.84, 0.48))
    column.add_child(kicker)
    title = Label.new()
    title.text = "FRONTLINE SURVIVAL"
    title.add_theme_font_size_override("font_size", 34)
    column.add_child(title)
    subtitle = Label.new()
    subtitle.add_theme_font_size_override("font_size", 15)
    subtitle.add_theme_color_override("font_color", Color(0.68, 0.77, 0.81))
    column.add_child(subtitle)
    var divider := HSeparator.new()
    column.add_child(divider)
    navigation = VBoxContainer.new()
    navigation.add_theme_constant_override("separation", 12)
    column.add_child(navigation)
    settings_tabs = HBoxContainer.new()
    settings_tabs.add_theme_constant_override("separation", 7)
    column.add_child(settings_tabs)
    _build_settings_tabs()
    options_scroll = ScrollContainer.new()
    options_scroll.custom_minimum_size = Vector2(645, 370)
    options_scroll.follow_focus = true
    options_scroll.horizontal_scroll_mode = ScrollContainer.SCROLL_MODE_DISABLED
    column.add_child(options_scroll)
    options = VBoxContainer.new()
    options.size_flags_horizontal = Control.SIZE_EXPAND_FILL
    options.add_theme_constant_override("separation", 8)
    options_scroll.add_child(options)
    footer = Label.new()
    footer.text = "MAPA DE TESTES  |  RYZEN 5 7530U  |  ESC: PAUSAR / VOLTAR"
    footer.add_theme_font_size_override("font_size", 12)
    footer.add_theme_color_override("font_color", Color(0.46, 0.56, 0.61))
    column.add_child(footer)

func _button(parent: Control, caption: String, callback: Callable, main_action: bool = false) -> void:
    var button := Button.new()
    button.text = caption
    button.custom_minimum_size = Vector2(340, 48)
    button.add_theme_font_size_override("font_size", 17)
    button.alignment = HORIZONTAL_ALIGNMENT_LEFT
    for state in ["normal","hover","pressed","focus"]:
        var style := StyleBoxFlat.new()
        style.bg_color = Color(0.24,0.27,0.17,0.95) if main_action or state != "normal" else Color(0.1,0.12,0.1,0.84)
        style.border_width_left = 3
        style.border_color = Color(0.84,0.85,0.48) if state != "normal" or main_action else Color(0.3,0.34,0.28)
        style.content_margin_left = 18
        style.set_corner_radius_all(1)
        button.add_theme_stylebox_override(state, style)
    button.pressed.connect(callback)
    parent.add_child(button)

func _build_settings_tabs() -> void:
    var categories := [
        ["graphics", "Vídeo"],
        ["audio", "Áudio"],
        ["controls", "Controles"],
        ["gameplay", "Partida"]
    ]
    for entry in categories:
        var button := Button.new()
        button.text = entry[1]
        button.toggle_mode = true
        var selected := StyleBoxFlat.new()
        selected.bg_color = Color(0.18, 0.20, 0.15)
        selected.border_width_bottom = 3
        selected.border_color = Color(0.84, 0.85, 0.48)
        button.add_theme_stylebox_override("pressed", selected)
        button.add_theme_stylebox_override("hover_pressed", selected)
        button.custom_minimum_size = Vector2(145, 38)
        button.size_flags_horizontal = Control.SIZE_EXPAND_FILL
        button.add_theme_font_size_override("font_size", 14)
        button.pressed.connect(_select_category.bind(entry[0]))
        settings_tabs.add_child(button)

func _select_category(id: String) -> void:
    settings_category = id
    _render()

func _bindings() -> void:
    var reveal := Button.new()
    reveal.text = "Ver comandos"
    reveal.toggle_mode = true
    options.add_child(reveal)
    var grid := GridContainer.new()
    grid.columns = 4
    grid.add_theme_constant_override("h_separation", 20)
    grid.add_theme_constant_override("v_separation", 7)
    options.add_child(grid)
    for pair in [
        ["Mover", "WASD"], ["Correr", "Shift"], ["Agachar", "C / Ctrl"], ["Deitar", "Z"],
        ["Pular", "Espaço"], ["Interagir", "F"], ["Atirar", "Mouse 1"], ["Mirar", "Mouse 2"],
        ["Recarregar", "R"], ["Corpo a corpo", "E"], ["Trocar arma", "1 / 2"], ["Granada", "G"],
        ["Esquadrão", "3"], ["Apoio aéreo", "4"], ["Antecipar onda", "N"], ["Pausar", "Esc"]
    ]:
        var action := Label.new()
        action.text = pair[0]
        action.size_flags_horizontal = Control.SIZE_EXPAND_FILL
        grid.add_child(action)
        var key := Label.new()
        key.text = pair[1]
        key.add_theme_color_override("font_color", Color(0.86, 0.87, 0.62))
        grid.add_child(key)
    grid.hide()
    reveal.toggled.connect(func(expanded: bool):
        grid.visible = expanded
        reveal.text = "Ocultar comandos" if expanded else "Ver comandos"
    )

func _build_options() -> void:
    for child in options.get_children():
        options.remove_child(child)
        child.queue_free()
    options_scroll.scroll_vertical = 0
    match settings_category:
        "graphics":
            _toggle("Tela cheia", "fullscreen", GameSettings.fullscreen)
            _toggle("Sincronização vertical (VSync)", "vsync", GameSettings.vsync)
            _slider("Escala de resolução", "render_scale", GameSettings.render_scale, 0.7, 1.0, 0.05)
            _slider("Campo de visão (FOV)", "fov", GameSettings.field_of_view, GameSettings.FOV_MIN, GameSettings.FOV_MAX, 1.0)
            _toggle("Exibir FPS", "fps", GameSettings.show_fps)
        "audio":
            _slider("Volume principal", "master", GameSettings.master_volume, 0, 100, 1)
            _slider("Armas e efeitos", "sfx", GameSettings.sfx_volume, 0, 100, 1)
            _slider("Interface e avisos", "ui", GameSettings.ui_volume, 0, 100, 1)
        "controls":
            _slider("Sensibilidade do mouse", "sensitivity", GameSettings.mouse_sensitivity, 0.35, 3.0, 0.05)
            _toggle("Inverter eixo vertical", "invert_y", GameSettings.invert_mouse_y)
            _bindings()
        "gameplay":
            _slider("Intervalo entre ondas", "intermission", float(GameSettings.intermission_seconds), 30, 120, 15)
            _toggle("Reanimar no Campo de Testes", "training_respawns", GameSettings.training_respawns)
            _toggle("Marcador de acerto", "hitmarker", GameSettings.hitmarker_enabled)
            _toggle("Direção do dano recebido", "damage_direction", GameSettings.damage_direction_enabled)
    var line := HSeparator.new()
    options.add_child(line)
    _button(options, "Voltar", _back_options)

func _slider(caption: String, key: String, current: float, minimum: float, maximum: float, step: float) -> void:
    var line := HBoxContainer.new()
    line.add_theme_constant_override("separation", 13)
    options.add_child(line)
    var label := Label.new()
    label.text = caption
    label.custom_minimum_size = Vector2(226, 46)
    label.add_theme_font_size_override("font_size", 14)
    line.add_child(label)
    var control := HSlider.new()
    control.name = "Setting_" + key
    control.custom_minimum_size = Vector2(195, 25)
    control.size_flags_horizontal = Control.SIZE_EXPAND_FILL
    control.min_value = minimum
    control.max_value = maximum
    control.step = step
    control.value = current
    line.add_child(control)
    var output := Label.new()
    output.name = "Value_" + key
    output.custom_minimum_size = Vector2(55, 26)
    output.text = _formatted(key, current)
    output.horizontal_alignment = HORIZONTAL_ALIGNMENT_RIGHT
    line.add_child(output)
    control.value_changed.connect(_on_slider_changed.bind(key, output))

func _formatted(key: String, value: float) -> String:
    if key == "sensitivity":
        return "%.2fx" % value
    if key == "fov":
        return "%d°" % roundi(value)
    if key == "intermission":
        return "%ds" % roundi(value)
    if key == "render_scale":
        return "%d%%" % roundi(value * 100.0)
    return "%d%%" % roundi(value)

func _on_slider_changed(value: float, key: String, output: Label) -> void:
    output.text = _formatted(key, value)
    GameSettings.set_value(key, value)

func _toggle(caption: String, key: String, current: bool) -> void:
    var toggle := CheckButton.new()
    toggle.custom_minimum_size.y = 46
    toggle.text = caption
    toggle.button_pressed = current
    toggle.toggled.connect(_on_toggle.bind(key))
    options.add_child(toggle)

func _on_toggle(enabled: bool, key: String) -> void:
    GameSettings.set_value(key, enabled)

func _back_options() -> void:
    in_options = false
    _render()

func _show_options() -> void:
    in_options = true
    settings_category = "graphics"
    _render()

func _render() -> void:
    for child in navigation.get_children():
        navigation.remove_child(child)
        child.queue_free()
    navigation.visible = not in_options
    settings_tabs.visible = in_options
    options_scroll.visible = in_options
    for index in range(settings_tabs.get_child_count()):
        (settings_tabs.get_child(index) as Button).button_pressed = (
            index == ["graphics", "audio", "controls", "gameplay"].find(settings_category)
        )
    backdrop.color = Color(0.02,0.03,0.025,0.19 if mode == "main" else 0.56)
    kicker.text = "FRONTLINE    /    SURVIVAL" if mode == "pause" else "OPERAÇÕES    /    SOLO"
    footer.text = "ESC   VOLTAR" if in_options or pending_action != "" else ""
    kicker.visible = not in_options
    subtitle.visible = not in_options
    footer.visible = not in_options and footer.text != ""
    if in_options:
        title.add_theme_font_size_override("font_size", 36)
        title.text = "Configurações"
        subtitle.text = ""
        _build_options()
        for tab in settings_tabs.get_children():
            if tab.button_pressed:
                tab.grab_focus()
        return
    if pending_action != "":
        title.text = "Confirmar"
        subtitle.text = "Substituir o checkpoint e começar de novo?" if pending_action == "new" else "O progresso após o último checkpoint será perdido."
        _button(navigation, "Voltar", _cancel_action, true)
        _button(navigation, "Confirmar", _confirm_action)
    elif mode == "main":
        title.text = "FRONTLINE SURVIVAL"
        title.add_theme_font_size_override("font_size", 52)
        subtitle.text = "Campo de testes   /   Sobrevivência por ondas"
        _button(navigation, "Novo jogo", _request.bind("new"), true)
        var label := "Carregar jogo   ·   Onda %02d" % (checkpoint_wave + 1) if checkpoint_wave >= 0 else "Carregar jogo   ·   Sem checkpoint"
        _button(navigation, label, load_requested.emit)
        (navigation.get_child(1) as Button).disabled = checkpoint_wave < 0
        _button(navigation, "Configurações", _show_options)
        _button(navigation, "Sair do jogo", _quit)
    else:
        title.text = "Partida pausada"
        title.add_theme_font_size_override("font_size", 36)
        subtitle.text = "Onda %02d    /    $%d" % [current_wave, balance]
        _button(navigation, "Retomar partida", resume, true)
        _button(navigation, "Configurações", _show_options)
        _button(navigation, "Voltar ao menu inicial", _request.bind("main"))
        _button(navigation, "Sair do jogo", _request.bind("quit"))
        footer.text = "Checkpoint automático ao concluir cada onda."
    footer.visible = footer.text != ""
    navigation.get_child(0).grab_focus()

func _request(action: String) -> void:
    if action == "new" and checkpoint_wave < 0:
        _start()
        return
    pending_action = action
    _render()

func _cancel_action() -> void:
    pending_action = ""
    _render()

func _confirm_action() -> void:
    var action := pending_action
    pending_action = ""
    match action:
        "new": _start()
        "main": _restart()
        "quit": _quit()

func open_main() -> void:
    mode = "main"
    _open()

func open_pause() -> void:
    mode = "pause"
    _open()

func _open() -> void:
    active = true
    in_options = false
    visible = true
    _render()
    Input.set_mouse_mode(Input.MOUSE_MODE_VISIBLE)
    get_tree().paused = true

func _start() -> void:
    _close()
    start_requested.emit()

func resume() -> void:
    _close()
    resume_requested.emit()

func _close() -> void:
    get_tree().paused = false
    visible = false
    active = false
    in_options = false
    Input.set_mouse_mode(Input.MOUSE_MODE_CAPTURED)

func _restart() -> void:
    _close()
    restart_requested.emit()

func _quit() -> void:
    get_tree().paused = false
    get_tree().quit()
