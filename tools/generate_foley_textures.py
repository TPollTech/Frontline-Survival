"""Generate deterministic weapon surface textures (NumPy and Pillow)."""
from pathlib import Path
import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
TEXTURES = ROOT / "assets" / "textures"
TEXTURES.mkdir(parents=True, exist_ok=True)
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


if __name__ == "__main__":
    texture("metal", False)
    texture("polymer", True)
    print("Generated 4 original weapon surface textures.")
