shader_type canvas_item;
void fragment() {
    vec2 p = (SCREEN_UV - 0.5) / SCREEN_PIXEL_SIZE;
    float radius = 0.45 / SCREEN_PIXEL_SIZE.y;
    float vignette = smoothstep(radius * 0.91, radius, length(p));
    float crosshair = 1.0 - smoothstep(0.45, 1.25, min(abs(p.x), abs(p.y)));
    COLOR = vec4(vec3(0.017), max(vignette, crosshair * 0.91));
}
