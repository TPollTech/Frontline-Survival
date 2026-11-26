"""Original, tileable surface-map candidates for 02-05 (not runtime-bound).

RGB base-color is a neutral sRGB multiplier for existing authored colours;
normal is tangent-space +Y, ORM stores absolute linear factors. Reuse the
canonical PBR library for serialization, provenance and material bindings.
"""
import math

# Lattice frequencies, relief, albedo variation and roughness variation.
STYLE = {
    "exposed_metal": (48, 5, .13, .045, .05),
    "painted_metal": (24, 24, .16, .045, .07),
    "polymer": (32, 32, .26, .08, .09),
    "rubber": (18, 18, .30, .065, .07),
    "wood": (13, 3, .21, .19, .13),
    "brass": (38, 8, .09, .055, .06),
}


def _lattice(x, y, seed):
    v = (x * 374761393 + y * 668265263 + seed * 2246822519) & 0xffffffff
    v = ((v ^ (v >> 13)) * 1274126177) & 0xffffffff
    return ((v ^ (v >> 16)) & 65535) / 65535


def _noise(u, v, nx, ny, seed):
    x, y = u * nx, v * ny
    ix, iy = math.floor(x), math.floor(y)
    a, b = x - ix, y - iy
    a, b = a * a * (3 - 2 * a), b * b * (3 - 2 * b)
    def at(dx, dy):
        return _lattice((ix + dx) % nx, (iy + dy) % ny, seed)
    return (1-b)*((1-a)*at(0, 0)+a*at(1, 0))+b*((1-a)*at(0, 1)+a*at(1, 1))


def height_at(profile, u, v, seed=205):
    nx, ny, _, _, _ = STYLE[profile]
    u, v = u % 1, v % 1
    if profile == "wood":
        warp = .045 * math.sin(math.tau * v) + .025 * (_noise(u, v, 3, 3, seed)-.5)
        vein = .5 + .5 * math.sin(math.tau * (nx*u + nx*warp))
        return .65 * vein + .35 * _noise(u+warp, v, nx, ny, seed+1)
    coarse = _noise(u, v, nx, ny, seed)
    fine = _noise(u, v, nx*2, ny*2, seed+1)
    return .76 * coarse + .24 * fine


def _byte(value):
    return max(0, min(255, int(value + .5)))


def surface_pixels(profile, factors, size=256, seed=205):
    """Return three RGB8 buffers; size must be a power of two in [64, 512]."""
    if profile not in STYLE or size not in (64, 128, 256, 512):
        raise ValueError("unknown profile or unsupported size")
    if type(seed) is not int or not 0 <= seed <= 0xffffffff:
        raise ValueError("invalid seed")
    metal, rough = (float(factors[k]) for k in ("metallic", "roughness"))
    if not (0 <= metal <= 1 and 0 <= rough <= 1):
        raise ValueError("invalid PBR factors")
    _, _, relief, contrast, roughness_variation = STYLE[profile]
    h = [height_at(profile, x/size, y/size, seed) for y in range(size) for x in range(size)]
    def at(x, y):
        return h[(y % size)*size + (x % size)]
    out = {key: bytearray() for key in ("base_color", "normal", "orm")}
    for y in range(size):
        for x in range(size):
            a = at(x, y)
            # Neutral multiplier; no baked direct lighting or colour tint.
            value = _byte(255 * (1 - contrast * (1-a)))
            out["base_color"].extend((value, value, value))
            out["orm"].extend((255, _byte(255*(rough+roughness_variation*(a-.5))), _byte(255*metal)))
            nx = -relief * (at(x+1, y)-at(x-1, y)) * size/128
            ny = relief * (at(x, y+1)-at(x, y-1)) * size/128
            length = math.sqrt(nx*nx + ny*ny + 1)
            out["normal"].extend(_byte(255*(q/length*.5+.5)) for q in (nx, ny, 1))
    return {key: bytes(value) for key, value in out.items()}


def build_library(profiles, size=256, seed=205):
    """Adapt candidates to canonical PBR objects; does not alter game assets."""
    from .pbr import MaterialLibrary, PBRMaterial, TextureData
    if set(profiles) != set(STYLE):
        raise ValueError("profile coverage mismatch")
    mats, textures = [], []
    for i, profile in enumerate(sorted(profiles)):
        s = (seed+i) & 0xffffffff
        maps = surface_pixels(profile, profiles[profile], size, s)
        ids = {role: profile+"_"+role for role in maps}
        for role, pixels in maps.items():
            textures.append(TextureData(ids[role], role, size, size, pixels,
                f"procedural:frontline-02-05:{profile}:size={size}:seed={s}", "CC0-1.0"))
        # ORM stores absolute factors; do not multiply by profile factors again.
        mats.append(PBRMaterial(profile, (1,1,1,1), 1., 1.,
            base_color_texture=ids["base_color"], orm_texture=ids["orm"],
            normal_texture=ids["normal"]))
    return MaterialLibrary(tuple(mats), tuple(textures))
