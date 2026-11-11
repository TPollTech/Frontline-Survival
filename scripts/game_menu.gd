extends CanvasLayer
class_name SurvivalGameMenu
## Tela inicial, pausa e menu de configuracoes. Funciona com a arvore pausada.

signal start_requested
signal pause_requested
signal resume_requested
signal restart_requested

var backdrop: ColorRect
var container: PanelContainer
var title: Label
var subtitle: Label
var navigation: VBoxContainer
var options: VBoxContainer
var options_scroll: ScrollContainer
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
        if in_options:
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
    var centered := CenterContainer.new()
    centered.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
    backdrop.add_child(centered)
    container = PanelContainer.new()
    container.custom_minimum_size = Vector2(615, 0)
    var style := StyleBoxFlat.new()
    style.bg_color = Color(0.055, 0.085, 0.105, 1.0)
    style.border_color = Color(0.13, 0.65, 0.73, 0.65)
    style.set_border_width_all(1)
    style.set_corner_radius_all(12)
    style.set_content_margin_all(20)
    container.add_theme_stylebox_override("panel", style)
    centered.add_child(container)
    var column := VBoxContainer.new()
    column.add_theme_constant_override("separation", 10)
    container.add_child(column)
    var kicker := Label.new()
    kicker.text = "FRONTLINE   /   SURVIVAL 0.9.11"
    kicker.add_theme_font_size_override("font_size", 15)
    kicker.add_theme_color_override("font_color", Color(0.34, 0.79, 0.85))
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
    options_scroll = ScrollContainer.new()
    options_scroll.custom_minimum_size = Vector2(545, 405)
    options_scroll.horizontal_scroll_mode = ScrollContainer.SCROLL_MODE_DISABLED
    column.add_child(options_scroll)
    options = VBoxContainer.new()
    options.size_flags_horizontal = Control.SIZE_EXPAND_FILL
    options.add_theme_constant_override("separation", 8)
    options_scroll.add_child(options)
    _build_options()
    var footer := Label.new()
    footer.text = "MAPA DE TESTES  |  RYZEN 5 7530U  |  ESC: PAUSAR / VOLTAR"
    footer.add_theme_font_size_override("font_size", 12)
    footer.add_theme_color_override("font_color", Color(0.46, 0.56, 0.61))
    column.add_child(footer)

func _button(parent: Control, caption: String, callback: Callable, main_action: bool = false) -> void:
    var button := Button.new()
    button.text = caption
    button.custom_minimum_size = Vector2(530, 42)
    button.add_theme_font_size_override("font_size", 17)
    if main_action:
        var style := StyleBoxFlat.new()
        style.bg_color = Color(0.13, 0.43, 0.51)
        style.set_corner_radius_all(5)
        button.add_theme_stylebox_override("normal", style)
    button.pressed.connect(callback)
    parent.add_child(button)

func _build_options() -> void:
    var section := Label.new()
    section.text = "AUDIO  |  volume aplicado imediatamente"
    section.add_theme_font_size_override("font_size", 16)
    options.add_child(section)
    _slider("Volume geral", "master", GameSettings.master_volume, 0, 100, 1)
    _slider("Tiros e explosoes", "sfx", GameSettings.sfx_volume, 0, 100, 1)
    _slider("Interface e acertos", "ui", GameSettings.ui_volume, 0, 100, 1)
    var spacer := HSeparator.new()
    options.add_child(spacer)
    var controls := Label.new()
    controls.text = "CONTROLES E VIDEO"
    controls.add_theme_font_size_override("font_size", 16)
    options.add_child(controls)
    _slider("Sensibilidade do mouse", "sensitivity", GameSettings.mouse_sensitivity, 0.35, 3.0, 0.05)
    _slider("Campo de visao (FOV)", "fov", GameSettings.field_of_view, 60.0, 100.0, 1.0)
    var layout_keys := Label.new()
    layout_keys.text = "TECLADO: mouse atira/mira  |  F interage  |  E corpo a corpo\n1/2 armas  |  G granada  |  3 esquadrao  |  4 ataque aereo\nR recarga  |  C agachar  |  Shift correr  |  Esc pausar"
    layout_keys.add_theme_color_override("font_color", Color(0.68, 0.78, 0.79))
    layout_keys.add_theme_font_size_override("font_size", 13)
    options.add_child(layout_keys)
    _toggle("Tela cheia", "fullscreen", GameSettings.fullscreen)
    _toggle("Mostrar FPS", "fps", GameSettings.show_fps)
    var pause_divider := HSeparator.new()
    options.add_child(pause_divider)
    var game := Label.new()
    game.text = "PARTIDA / ONDAS"
    game.add_theme_font_size_override("font_size", 16)
    options.add_child(game)
    _slider("Intervalo entre ondas", "intermission", float(GameSettings.intermission_seconds), 45, 120, 15)
    _toggle("Reanimacao automatica no Campo de Testes", "training_respawns", GameSettings.training_respawns)
    var tip := Label.new()
    tip.text = "Teste: ondas sem limite e retorno ao combate apos cair.\nDesative a reanimacao para testar o modo classico (uma vida)."
    tip.add_theme_color_override("font_color", Color(0.62, 0.72, 0.77))
    tip.add_theme_font_size_override("font_size", 13)
    options.add_child(tip)
    _button(options, "VOLTAR", _back_options)

func _slider(caption: String, key: String, current: float, minimum: float, maximum: float, step: float) -> void:
    var line := HBoxContainer.new()
    line.add_theme_constant_override("separation", 13)
    options.add_child(line)
    var label := Label.new()
    label.text = caption
    label.custom_minimum_size = Vector2(220, 26)
    label.add_theme_font_size_override("font_size", 14)
    line.add_child(label)
    var control := HSlider.new()
    control.custom_minimum_size = Vector2(195, 25)
    control.size_flags_horizontal = Control.SIZE_EXPAND_FILL
    control.min_value = minimum
    control.max_value = maximum
    control.step = step
    control.value = current
    line.add_child(control)
    var output := Label.new()
    output.custom_minimum_size = Vector2(55, 26)
    output.text = _formatted(key, current)
    output.horizontal_alignment = HORIZONTAL_ALIGNMENT_RIGHT
    line.add_child(output)
    control.value_changed.connect(_on_slider_changed.bind(key, output))

func _formatted(key: String, value: float) -> String:
    if key == "sensitivity":
        return "%.2fx" % value
    if key == "fov":
        return "%d" % roundi(value)
    if key == "intermission":
        return "%ds" % roundi(value)
    return "%d%%" % roundi(value)

func _on_slider_changed(value: float, key: String, output: Label) -> void:
    output.text = _formatted(key, value)
    GameSettings.set_value(key, value)

func _toggle(caption: String, key: String, current: bool) -> void:
    var toggle := CheckButton.new()
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
    _render()

func _render() -> void:
    for child in navigation.get_children():
        navigation.remove_child(child)
        child.queue_free()
    navigation.visible = not in_options
    options_scroll.visible = in_options
    if in_options:
        title.text = "CONFIGURACOES"
        subtitle.text = "Ajuste audio, mouse e visual sem sair da partida."
    elif mode == "main":
        title.text = "SURVIVAL"
        subtitle.text = "Ondas continuas / 3 arsenais fisicos / suporte sob comando"
        _button(navigation, "INICIAR PARTIDA", _start, true)
        _button(navigation, "CONFIGURACOES", _show_options)
        _button(navigation, "SAIR DO JOGO", _quit)
    else:
        title.text = "JOGO PAUSADO"
        subtitle.text = "A acao esta congelada enquanto o menu estiver aberto."
        _button(navigation, "CONTINUAR", resume, true)
        _button(navigation, "CONFIGURACOES", _show_options)
        _button(navigation, "REINICIAR PARTIDA", _restart)
        _button(navigation, "SAIR DO JOGO", _quit)

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
