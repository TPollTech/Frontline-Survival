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
    container.custom_minimum_size = Vector2(710, 0)
    var style := StyleBoxFlat.new()
    style.bg_color = Color(0.035, 0.061, 0.079, 0.98)
    style.border_color = Color(0.21, 0.64, 0.71, 0.62)
    style.set_border_width_all(1)
    style.set_corner_radius_all(12)
    style.set_content_margin_all(24)
    container.add_theme_stylebox_override("panel", style)
    centered.add_child(container)
    var column := VBoxContainer.new()
    column.add_theme_constant_override("separation", 10)
    container.add_child(column)
    var kicker := Label.new()
    kicker.text = "FRONTLINE   /   SURVIVAL 0.9.18"
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
    settings_tabs = HBoxContainer.new()
    settings_tabs.add_theme_constant_override("separation", 7)
    column.add_child(settings_tabs)
    _build_settings_tabs()
    options_scroll = ScrollContainer.new()
    options_scroll.custom_minimum_size = Vector2(645, 370)
    options_scroll.horizontal_scroll_mode = ScrollContainer.SCROLL_MODE_DISABLED
    column.add_child(options_scroll)
    options = VBoxContainer.new()
    options.size_flags_horizontal = Control.SIZE_EXPAND_FILL
    options.add_theme_constant_override("separation", 8)
    options_scroll.add_child(options)
    var footer := Label.new()
    footer.text = "MAPA DE TESTES  |  RYZEN 5 7530U  |  ESC: PAUSAR / VOLTAR"
    footer.add_theme_font_size_override("font_size", 12)
    footer.add_theme_color_override("font_color", Color(0.46, 0.56, 0.61))
    column.add_child(footer)

func _button(parent: Control, caption: String, callback: Callable, main_action: bool = false) -> void:
    var button := Button.new()
    button.text = caption
    button.custom_minimum_size = Vector2(605, 44)
    button.add_theme_font_size_override("font_size", 17)
    if main_action:
        var style := StyleBoxFlat.new()
        style.bg_color = Color(0.13, 0.43, 0.51)
        style.set_corner_radius_all(5)
        button.add_theme_stylebox_override("normal", style)
    button.pressed.connect(callback)
    parent.add_child(button)

func _build_settings_tabs() -> void:
    var categories := [
        ["graphics", "GRAFICOS"],
        ["audio", "AUDIO"],
        ["controls", "CONTROLES"],
        ["gameplay", "JOGABILIDADE"]
    ]
    for entry in categories:
        var button := Button.new()
        button.text = entry[1]
        button.toggle_mode = true
        button.custom_minimum_size = Vector2(145, 38)
        button.size_flags_horizontal = Control.SIZE_EXPAND_FILL
        button.add_theme_font_size_override("font_size", 14)
        button.pressed.connect(_select_category.bind(entry[0]))
        settings_tabs.add_child(button)

func _select_category(id: String) -> void:
    settings_category = id
    _render()

func _heading(caption: String) -> void:
    var label := Label.new()
    label.text = caption
    label.add_theme_font_size_override("font_size", 19)
    label.add_theme_color_override("font_color", Color(0.38, 0.84, 0.88))
    options.add_child(label)

func _note(caption: String) -> void:
    var label := Label.new()
    label.text = caption
    label.custom_minimum_size = Vector2(540, 0)
    label.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
    label.add_theme_font_size_override("font_size", 13)
    label.add_theme_color_override("font_color", Color(0.64, 0.74, 0.77))
    options.add_child(label)

func _build_options() -> void:
    for child in options.get_children():
        options.remove_child(child)
        child.queue_free()
    options_scroll.scroll_vertical = 0
    match settings_category:
        "graphics":
            _heading("VIDEO E DESEMPENHO")
            _note("Graficos leves para o Ryzen 5 7530U. Alteracoes aplicadas na hora.")
            _toggle("Tela cheia", "fullscreen", GameSettings.fullscreen)
            _toggle("Sincronizacao vertical (VSync)", "vsync", GameSettings.vsync)
            _slider("Escala da imagem 3D", "render_scale", GameSettings.render_scale, 0.7, 1.0, 0.05)
            _toggle("Mostrar contador de FPS", "fps", GameSettings.show_fps)
            _note("70-80% aumenta o desempenho, mas reduz nitidez; 100% preserva a resolucao.")
        "audio":
            _heading("MIXAGEM DE AUDIO")
            _note("Sem apitos de hitmarker. Disparos e recargas usam arquivos WAV do projeto.")
            _slider("Volume principal", "master", GameSettings.master_volume, 0, 100, 1)
            _slider("Armas e efeitos", "sfx", GameSettings.sfx_volume, 0, 100, 1)
            _slider("Interface e avisos", "ui", GameSettings.ui_volume, 0, 100, 1)
            _note("Sugestao para o notebook: geral 48%, armas 28%, interface 42%.")
        "controls":
            _heading("MOUSE E CONTROLES")
            _slider("Sensibilidade do mouse", "sensitivity", GameSettings.mouse_sensitivity, 0.35, 3.0, 0.05)
            _toggle("Inverter eixo vertical do mouse", "invert_y", GameSettings.invert_mouse_y)
            _note("WASD mover  |  Shift correr  |  C/Ctrl agachar  |  Z deitar\nMouse esquerdo atirar  |  Direito mirar  |  R recarregar\nF interagir/comprar  |  E corpo a corpo  |  G granada\n1/2 trocar arma  |  3 esquadrao  |  4 apoio aereo\nN antecipar onda na preparacao  |  Esc pausar/voltar")
            _note("Remapeamento individual de teclas fica para uma etapa posterior.")
        "gameplay":
            _heading("PARTIDA E INTERFACE")
            _slider("Tempo de preparacao", "intermission", float(GameSettings.intermission_seconds), 30, 120, 15)
            _toggle("Reanimar no Campo de Testes", "training_respawns", GameSettings.training_respawns)
            _toggle("Hitmarker discreto ao acertar", "hitmarker", GameSettings.hitmarker_enabled)
            _toggle("Indicadores vermelhos de dano", "damage_direction", GameSettings.damage_direction_enabled)
            _note("Onda continua automaticamente. No modo classico, a morte encerra a partida.\nPerks, attachments e ultima chance continuam funcionando.")
    var line := HSeparator.new()
    options.add_child(line)
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
    if key == "render_scale":
        return "%d%%" % roundi(value * 100.0)
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
    if in_options:
        title.text = "CONFIGURACOES"
        subtitle.text = "GRAFICOS  /  AUDIO  /  CONTROLES  /  JOGABILIDADE"
        _build_options()
    elif mode == "main":
        title.text = "SURVIVAL"
        subtitle.text = "CAMPO DE TESTES  |  OPERACAO SOLO  |  PROGRESSAO POR ONDAS"
        _button(navigation, "JOGAR  /  INICIAR OPERACAO", _start, true)
        _button(navigation, "CONFIGURACOES", _show_options)
        _button(navigation, "ENCERRAR JOGO", _quit)
    else:
        title.text = "OPERACAO PAUSADA"
        subtitle.text = "A partida esta pausada. Ajustes salvos automaticamente."
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
