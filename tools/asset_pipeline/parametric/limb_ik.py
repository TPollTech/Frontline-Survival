"""Analytic two-bone IK candidate for the canonical rig.

Positions share one coordinate frame. Flexion is zero at full extension.
Returns joint positions, not engine bone rotations or skin weights.
The caller owns anatomical limits, pole continuity and integration.
"""
from dataclasses import dataclass
import math


def _vec(value):
    v = tuple(float(x) for x in value)
    if len(v) != 3 or not all(math.isfinite(x) for x in v):
        raise ValueError("expected finite 3-vector")
    return v


def _add(a, b):
    return tuple(x + y for x, y in zip(a, b))


def _sub(a, b):
    return tuple(x - y for x, y in zip(a, b))


def _mul(a, s):
    return tuple(x * s for x in a)


def _dot(a, b):
    return sum(x * y for x, y in zip(a, b))


def _unit(a):
    n = math.hypot(*a)
    if n <= 1e-10:
        raise ValueError("undefined direction")
    return _mul(a, 1 / n)


def _project(v, axis):
    return _sub(v, _mul(axis, _dot(v, axis)))


@dataclass(frozen=True)
class LimbSolution:
    elbow: tuple
    wrist: tuple
    flexion: float
    target_error: float
    clamped: bool
    bend_direction: tuple


def solve_limb(root, target, pole, upper, lower, *, min_flexion=.02,
               max_flexion=2.5, previous_bend=None, fallback_axis=None):
    """Reach the nearest allowed target, preserving both bone lengths.

    pole is a point. previous_bend is an optional direction (same frame)
    for degenerate poles; fallback_axis is required at a coincident target.
    Singular inputs without an explicit fallback are rejected, not guessed.
    Limits are provisional caller-supplied radians, not medical measurements.
    """
    root, target, pole = map(_vec, (root, target, pole))
    upper, lower, lo, hi = map(float, (upper, lower, min_flexion, max_flexion))
    if not all(math.isfinite(x) for x in (upper, lower, lo, hi)) or not (
            upper > 1e-6 and lower > 1e-6 and 0 < lo <= hi < math.pi):
        raise ValueError("invalid lengths or flexion limits")
    delta = _sub(target, root)
    distance = math.hypot(*delta)
    if distance <= 1e-10:
        if fallback_axis is None:
            raise ValueError("coincident target requires fallback axis")
        axis = _unit(_vec(fallback_axis))
    else:
        axis = _unit(delta)
    bend = _project(_sub(pole, root), axis)
    if math.hypot(*bend) <= 1e-10:
        if previous_bend is None:
            raise ValueError("degenerate pole requires previous bend")
        bend = _project(_vec(previous_bend), axis)
    bend = _unit(bend)
    def reach(flex):
        return math.hypot(upper + lower * math.cos(flex), lower * math.sin(flex))
    nearest, farthest = reach(hi), reach(lo)
    d = max(nearest, min(farthest, distance))
    flex = math.acos(max(-1., min(1., (d*d-upper*upper-lower*lower)/(2*upper*lower))))
    along = (d*d + upper*upper - lower*lower)/(2*d)
    height = math.sqrt(max(0., upper*upper - along*along))
    elbow = _add(root, _add(_mul(axis, along), _mul(bend, height)))
    wrist = _add(root, _mul(axis, d))
    error = math.hypot(*_sub(wrist, target))
    return LimbSolution(elbow, wrist, flex, error, distance < nearest or distance > farthest, bend)
