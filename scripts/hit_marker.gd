extends Control
## A 150ms confirmation only when a real enemy is hit.
## No permanent crosshair and no audio chirp.
var remaining: float = 0.0
var headshot: bool = false

func _ready() -> void:
    mouse_filter = Control.MOUSE_FILTER_IGNORE
    visible = false
    set_process(true)

func flash(is_headshot: bool = false) -> void:
    remaining = 0.16
    headshot = headshot or is_headshot
    visible = true
    queue_redraw()

func _process(delta: float) -> void:
    if remaining <= 0.0:
        visible = false
        headshot = false
        return
    remaining = maxf(0.0, remaining - delta)
    modulate.a = minf(0.80, remaining * 6.2)
    queue_redraw()

func _draw() -> void:
    var color := Color(1.0, 0.75, 0.42) if headshot else Color(0.96, 0.97, 0.95)
    var inner: float = 4.5
    var outer: float = 11.0
    for sx in [-1.0, 1.0]:
        for sy in [-1.0, 1.0]:
            draw_line(
                Vector2(sx * inner, sy * inner),
                Vector2(sx * outer, sy * outer),
                color, 1.65, true
            )
