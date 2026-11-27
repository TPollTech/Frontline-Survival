"""Original 02-06 hand-shape candidates, independent of the existing joint rig.

Every mesh is a closed canonical OrganicLoft. Local Y is the long axis;
callers must retain existing joint transforms and validate the FPS poses.
No engine integration, skin weights, texture authoring or attachment policy.
"""
from .model import number, require
from .organic import LoftSection, OrganicLoft, build_organic

# Relative radii: index, middle, ring, little; thumb handled separately.
FINGER_RADII = (0.0132, 0.0140, 0.0128, 0.0105)


def _mesh(id, sections, sides, steps, power):
    return build_organic(OrganicLoft(id, tuple(LoftSection(y, (x, z), (rx, rz))
        for y, x, z, rx, rz in sections), sides, steps, power))


def palm(right=True):
    """Asymmetric padded palm; mirror the cross-section centre, not winding."""
    require(type(right) is bool, "expected hand side")
    s = 1 if right else -1
    rows = [(-.075, .000, .000, .026, .018),
            (-.060, .004, .000, .038, .025),
            (-.032, .008, .003, .046, .029),
            ( .000, .004, .002, .051, .030),
            ( .028, .001, .000, .050, .028),
            ( .050, -.003, .000, .046, .023),
            ( .068, -.004, .000, .037, .017),
            ( .075, -.004, .000, .025, .010)]
    return _mesh("fps_palm_right" if right else "fps_palm_left",
                 [(y,s*x,z,rx,rz) for y,x,z,rx,rz in rows], 24, 2, 3.2)


def dorsal_panel():
    """Low padded dorsal panel, not a round sphere."""
    return _mesh("fps_dorsal_panel", [(-.047,0,0,.018,.003),
        (-.033,0,0,.042,.011), (0,0,0,.047,.013),
        (.033,0,0,.043,.010), (.047,0,0,.019,.003)], 20, 2, 3.1)


def finger_segment(digit, distal, axis_length):
    """Tapered joint-local segment with overlap at the ends; digit 4 is thumb."""
    require(type(digit) is int and 0 <= digit <= 4 and type(distal) is bool,
            "invalid digit or segment")
    length = number(axis_length)
    require(length > .005, "segment too short")
    radius = .020 if digit == 4 else FINGER_RADII[digit]
    radius *= .78 if distal else 1.0
    # Extend past each joint to avoid an immediate seam at the existing pivot.
    # The joint centres and animation angles are not changed by the recipe.
    r = radius
    h = length/2
    rows = [(-h-r*.70,0,0,r*.35,r*.32),
            (-h,0,0,r*.95,r*.83), (-h*.35,0,0,r,r*.86),
            (h*.30,0,0,r*.92,r*.80), (h,0,0,r*.81,r*.70),
            (h+r*.55,0,0,r*.14,r*.13)]
    return _mesh(f"fps_digit_{digit}_{'distal' if distal else 'proximal'}",
                 rows, 16, 1, 2.2)


def sleeve(id, axis_length, top_radius, bottom_radius):
    """Tapered cloth volume with asymmetric sections and cuff overlap."""
    length, top, bottom = map(number, (axis_length, top_radius, bottom_radius))
    require(length > .02 and min(top,bottom) > .005, "invalid sleeve dimensions")
    full = length + min(top,bottom)*.7
    rows = []
    for t, factor, shift in ((0,.90,0),(.09,1.04,.02),(.17,.99,-.02),
                             (.32,1.10,.04),(.51,1.05,-.03),(.74,1.00,.02),
                             (.86,1.07,0),(1,.90,0)):
        r = (bottom+(top-bottom)*t)*factor
        rows.append(((t-.5)*full, shift*r, -.03*r, r, r*.84))
    return _mesh(id, rows, 20, 1, 2.35)
