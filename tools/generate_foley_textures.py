"""Deterministic original low-cost weapon surface textures and mechanical reload foley.

Outputs are generated in CI and committed with the GLBs. Requires numpy/Pillow.
No external weapon recordings or licensed assets.
"""
from pathlib import Path
import wave
import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
TEXTURES = ROOT / "assets" / "textures"
RELOADS = ROOT / "assets" / "audio" / "reloads"
TEXTURES.mkdir(parents=True, exist_ok=True)
RELOADS.mkdir(parents=True, exist_ok=True)
rng = np.random.default_rng(9133)
SIZE = 256

def texture(name: str, polymer: bool):
    yy, xx = np.mgrid[:SIZE, :SIZE].astype(np.float32)
    noise = rng.normal(0, 1, (SIZE, SIZE)).astype(np.float32)
    horizontal = rng.normal(0, 1, (SIZE, 1)).astype(np.float32)
    scratches = (np.sin(xx * 0.42 + np.sin(yy * 0.05)) * 0.016)
    if polymer:
        grain = np.clip(0.86 + noise * 0.025 + np.sin(yy * 1.1) * 0.013, .67, .95)
    else:
        grain = np.clip(0.81 + horizontal * .019 + scratches + noise * .022, .65, .97)
    # Neutral grayscale multiplies the glTF COLOR_0 palette without washing it out.
    alb = (grain * 255).astype(np.uint8)
    Image.fromarray(np.repeat(alb[:, :, None], 3, axis=2), "RGB").save(
        TEXTURES / f"weapon_{name}_albedo.png", optimize=True
    )
    grad_y, grad_x = np.gradient(grain)
    strength = 2.4 if polymer else 1.9
    normal = np.stack([-grad_x * strength, -grad_y * strength, np.ones_like(grain)], axis=2)
    normal /= np.maximum(1e-6, np.linalg.norm(normal, axis=2, keepdims=True))
    rgb = np.clip((normal * 0.5 + 0.5) * 255, 0, 255).astype(np.uint8)
    Image.fromarray(rgb, "RGB").save(TEXTURES / f"weapon_{name}_normal.png", optimize=True)

SR = 22050

def click(dur: float, pitch: float = 650.0, mass: float = 1.0):
    n = int(dur * SR)
    t = np.arange(n, dtype=np.float32) / SR
    crackle = rng.standard_normal(n).astype(np.float32)
    # Mechanical impulse: low-mid resonance plus a short, filtered metal snap.
    tone = np.sin(2 * np.pi * (pitch - 90 * t) * t)
    raw = tone * .38 + crackle * .31
    filt = np.convolve(raw, np.ones(7, dtype=np.float32) / 7, mode="same")
    envelope = (1 - np.exp(-t * 2100)) * np.exp(-t * 42)
    return (filt * envelope * mass).astype(np.float32)

def slide(dur: float, base: float = 180.0):
    n = int(dur * SR)
    t = np.arange(n, dtype=np.float32) / SR
    noise = rng.standard_normal(n).astype(np.float32)
    scrape = np.convolve(noise, np.ones(19, dtype=np.float32) / 19, mode="same")
    harmonics = np.sin(2 * np.pi * base * t + 10 * np.sin(2 * np.pi * 18 * t))
    shape = np.sin(np.pi * t / max(dur, 0.01)) ** 2
    return ((scrape * .48 + harmonics * .055) * shape).astype(np.float32)

def write_wav(name: str, seconds: float, events):
    samples = np.zeros(int(seconds * SR), dtype=np.float32)
    for start, kind, duration, level, pitch in events:
        sound = click(duration, pitch, 1.0) if kind == "click" else slide(duration, pitch)
        offset = int(start * SR)
        length = min(len(sound), len(samples) - offset)
        if length > 0:
            samples[offset:offset + length] += sound[:length] * level
    # Mild room resonance and soft limiter; no chirps or synthetic alert tones.
    delay = int(SR * .037)
    original = samples.copy()
    samples[delay:] += original[:-delay] * .16
    samples = np.tanh(samples * 1.8) * .58
    pcm = (np.clip(samples, -1, 1) * 32767).astype("<i2")
    with wave.open(str(RELOADS / f"{name}.wav"), "wb") as output:
        output.setnchannels(1)
        output.setsampwidth(2)
        output.setframerate(SR)
        output.writeframes(pcm.tobytes())

texture("metal", False)
texture("polymer", True)

clips = {
    "pistol": (1.20, [(0.03, "click", .07, .95, 850), (.16, "slide", .18, .65, 215), (.39, "click", .08, .90, 630), (.70, "click", .10, .65, 740)]),
    "smg": (1.60, [(0.05, "click", .07, .82, 720), (.22, "slide", .32, .72, 190), (.66, "click", .07, .85, 880), (1.05, "click", .10, .90, 610)]),
    "rifle": (1.85, [(0.04, "click", .08, .90, 580), (.20, "slide", .38, .75, 175), (.80, "click", .10, .95, 650), (1.20, "slide", .17, .48, 230), (1.50, "click", .10, .84, 740)]),
    "shotgun": (2.05, [(0.03, "click", .08, .76, 480), (.35, "slide", .28, .86, 160), (.85, "click", .07, .65, 750), (1.15, "click", .08, .72, 700), (1.57, "slide", .22, .66, 160), (1.80, "click", .09, .78, 540)]),
    "lmg": (3.50, [(0.07, "click", .11, .85, 470), (.38, "slide", .52, .80, 155), (1.16, "click", .09, .95, 570), (1.65, "slide", .37, .75, 175), (2.27, "click", .08, .74, 740), (2.91, "click", .11, .88, 530)]),
}
for key, (seconds, events) in clips.items():
    write_wav(key, seconds, events)

print("Generated 4 original surface textures and 5 mechanical reload WAVs.")
