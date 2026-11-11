"""Static project verifier for Frontline Survival 0.7.

Run: python tools/verify_project.py
Checks script structure, core gameplay invariants, geometry groups and WAV files.
This is NOT a Godot import, parse or gameplay test.
"""
from pathlib import Path
from collections import Counter
from hashlib import sha256
import re
import wave
import sys

import numpy as np
import trimesh

ROOT = Path(__file__).resolve().parents[1]
errors = []
notes = []


def require(ok, explanation):
    if not ok:
        errors.append(explanation)


def inspect_script(path):
    source = path.read_text(encoding="utf-8")
    require("\t" not in source, f"Tabs in {path.name}")
    functions = re.findall(r"^func\s+(\w+)\(", source, re.M)
    repeated = [n for n, count in Counter(functions).items() if count > 1]
    require(not repeated, f"Duplicate functions in {path.name}: {repeated}")

    # Balance brackets, respecting strings and line comments.
    open_to_close = {"(": ")", "[": "]", "{": "}"}
    closers = set(open_to_close.values())
    stack = []
    in_quote = False
    escaped = False
    in_comment = False
    for index, char in enumerate(source):
        if char == "\n":
            in_comment = False
            continue
        if in_comment:
            continue
        if in_quote:
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == '"':
                in_quote = False
            continue
        if char == '#':
            in_comment = True
        elif char == '"':
            in_quote = True
        elif char in open_to_close:
            stack.append((char, index))
        elif char in closers:
            if not stack or open_to_close[stack[-1][0]] != char:
                errors.append(f"Unexpected bracket {char} at {path.name}:{index}")
                break
            stack.pop()
    require(not stack and not in_quote, f"Unclosed string or bracket in {path.name}")

    for number, line in enumerate(source.splitlines(), 1):
        indent = len(line) - len(line.lstrip(' '))
        if indent % 4 != 0 and line.strip():
            # A few aligned continuation lines are valid GDScript.
            if not line.strip().startswith(("palm_location", "0.014", "0.021")):
                errors.append(f"Suspicious indentation {path.name}:{number}")

    for resource in re.findall(r'"res://([^"%]+)"', source):
        require((ROOT / resource).is_file(), f"Missing resource {resource}, referenced by {path.name}")
    return source


sources = {p.stem: inspect_script(p) for p in (ROOT / "scripts").glob("*.gd")}
require(len(sources) >= 7, "Expected 7+ game scripts")
main = sources["main"]
player = sources["player"]
enemy = sources["enemy"]
ally = sources["ally"]
settings = sources["game_settings"]

# These are regression checks for the exact issues reported during the project.
for fragment in (
    '"weapons":', '"gear":', '"support":',
    'func _begin_wave(', 'func _end_wave(',
    'GameSettings.intermission_seconds',
    'func _nearest_shop(', 'KEY_F', 'KEY_3', 'KEY_4',
    'GameSettings.training_respawns',
    'player.revive_for_testing()',
):
    require(fragment in main, f"Missing continuous-survival feature: {fragment}")
require("KEY_B" not in main, "Fast-shop B was restored by mistake")
require("crosshair_h" not in main and "crosshair_v" not in main,
        "Hardcore aiming: 2D crosshair accidentally restored")
require("hit_audio" not in main and "round_audio.play()" in main,
        "Irritating hit-confirmation beep must stay disabled; soft wave cue required")
require('res://assets/audio/round_clear.wav' in main and (ROOT / "assets/audio/round_clear.wav").is_file(),
        "Soft synthesized wave cue missing")
require("sight_height" in player and "camera.rotation.x = clampf" in player,
        "Physical sight alignment and camera recoil fix missing")
require("KEY_F" not in player, "F should be interaction only, never shoot")
for fragment in ('func _animate_viewmodel(', 'magazine_part.position', 'action_part.position', 'reload_elapsed', 'shot_anim'):
    require(fragment in player, f"Weapon animation missing: {fragment}")
for fragment in ('LeftHip', 'RightHip', 'Knee', 'Elbow', 'func take_damage(', 'stagger_remaining', 'visual_root', 'ArmPose.align_hand('):
    require(fragment in enemy, f"Articulated enemy animation missing: {fragment}")
for fragment in ('LeftHip', 'RightHip', 'FriendlyPatch', 'func _physics_process(', 'ArmPose.align_hand('):
    require(fragment in ally, f"Ally visual or AI missing: {fragment}")
for fragment in ('viewmodel_scale', 'viewmodel_depth', 'GunMaterials.apply_colors'):
    require(fragment in player, f"Weapon viewmodel repair missing: {fragment}")
require("GunMaterials.apply_colors" in enemy and "GunMaterials.apply_colors" in ally,
        "NPC weapon palette setup missing")
material_code = (ROOT / 'scripts/weapon_materials.gd').read_text(encoding='utf-8')
require('vertex_color_use_as_albedo = true' in material_code,
        "Godot imported weapon models must use glTF vertex color attribute COLOR_0")
pose_code = (ROOT / 'scripts/weapon_pose.gd').read_text(encoding='utf-8')
require('func align_hand(' in pose_code and 'upper_length' in pose_code,
        "Shared two-bone arm solver missing")
require('intermission_seconds: int = 75' in settings, "Default break should still be 75 seconds")
require('training_respawns: bool = true' in settings, "Training respawn should remain enabled")
require('1280' in (ROOT / 'project.godot').read_text(), "Missing 720p target")
require('gl_compatibility' in (ROOT / 'project.godot').read_text(), "Rendering must target Compatibility")
require((ROOT / 'scenes/main.tscn').exists(), "Missing main scene")

models = ROOT / 'assets/models'
weapons = ['pistol','smg','rifle','shotgun','lmg']
# Godot can render imported GLBs white unless COLOR_0 is enabled by a material.
# All source geometry is expected to preserve the color attribute.
for weapon in weapons:
    full = models / f'{weapon}.glb'
    require(full.is_file(), f"Missing merged {weapon} GLB")
    if not full.is_file():
        continue
    try:
        original = trimesh.load(full, force='scene')
        whole_faces = sum(len(mesh.faces) for mesh in original.geometry.values())
        # Regression guard: inverted face winding makes imported Godot weapons
        # look hollow/transparent due to back-face culling.
        require(all(mesh.volume > 0 for mesh in original.geometry.values()),
                f"Inward normals detected in {weapon}.glb")
        group_faces = 0
        groups_present = []
        for role in ['body','mag','action']:
            part = models / f'{weapon}_{role}.glb'
            if not part.is_file():
                require(role == 'mag' and weapon == 'shotgun', f"Missing {weapon}_{role}.glb")
                continue
            scene = trimesh.load(part, force='scene')
            require(bool(scene.geometry), f"Empty mesh group in {part.name}")
            group_faces += sum(len(mesh.faces) for mesh in scene.geometry.values())
            groups_present.append(role)
        require(group_faces == whole_faces, f"Broken mesh grouping: {weapon}: {group_faces}/{whole_faces} faces")
        notes.append(f"{weapon}: {whole_faces} triangles, {','.join(groups_present)}")
    except Exception as exc:
        errors.append(f"GLB parse error in {weapon}: {exc}")

for weapon in weapons:
    path = ROOT / f'assets/audio/weapons/{weapon}.wav'
    require(path.exists(), f"Missing new {weapon}.wav")
    if not path.exists():
        continue
    try:
        with wave.open(str(path), 'rb') as reader:
            require(reader.getnchannels() == 1 and reader.getsampwidth() == 2, f"Invalid WAV format in {weapon}")
            frames = reader.readframes(reader.getnframes())
            audio = np.frombuffer(frames, dtype='<i2') / 32768.0
            peak = float(np.max(abs(audio))) if audio.size else 0
            length = reader.getnframes() / reader.getframerate()
            require(0.03 < peak <= 0.65, f"Suspicious/unsafe peak in {weapon}: {peak:.2f}")
            require(0.10 < length < 0.8, f"Suspicious sound duration in {weapon}: {length:.2f}")
            notes.append(f"{weapon} shot: peak={peak:.3f}, duration={length:.2f}s")
    except Exception as exc:
        errors.append(f"WAV parse error in {weapon}: {exc}")

# Regression guards for 0.9.3: textured weapons, connected allied head,
# distinct mechanical reloads and inexpensive local obstacle steering.
for png in (
    "weapon_metal_albedo.png", "weapon_polymer_albedo.png",
    "weapon_metal_normal.png", "weapon_polymer_normal.png"
):
    texture = ROOT / "assets" / "textures" / png
    require(texture.is_file() and texture.stat().st_size > 300,
            f"Missing generated weapon texture: {png}")
for weapon in weapons:
    reload_file = ROOT / "assets" / "audio" / "reloads" / f"{weapon}.wav"
    require(reload_file.exists(), f"Missing mechanical reload foley: {weapon}")
    if reload_file.exists():
        with wave.open(str(reload_file), "rb") as sound:
            length = sound.getnframes() / float(sound.getframerate())
            samples = np.frombuffer(sound.readframes(sound.getnframes()), dtype="<i2")
            peak = np.max(np.abs(samples.astype(np.float32))) / 32768.0
            require(0.3 < length < 4.0 and 0.005 < peak < 0.82,
                    f"Invalid reload sound parameters: {weapon}")
require('HeadPivot' in ally and 'NeckCollar' in ally,
        "Support soldier head could separate from collar again")
require('ObstacleSteering.choose_detour' in enemy and 'ObstacleSteering.choose_detour' in ally,
        "Local obstacle-recovery steering must work for enemies and allies")
require('reload_sound.stream = WeaponAudio.reload_for(weapon_id)' in player,
        "Different weapon reloads should use their own mechanical WAV")
require('material.albedo_texture = load(' in material_code and 'material.uv1_triplanar = true' in material_code,
        "Textured gun materials with triplanar mapping missing")

expected_asphalt_hash = 'be44732a105d975100d827f166da25dd5159a89760e3b3cd0cdcbb5683e1d29a'
require(sha256((ROOT/'assets/textures/asphalt.png').read_bytes()).hexdigest() == expected_asphalt_hash,
        "Original asphalt texture was modified")

print('\n'.join(notes))
print(f"\nStatic tests: {len(list(ROOT.rglob('*.gd')))} scripts, {len(list(ROOT.rglob('*.glb')))} GLBs, {len(list(ROOT.rglob('*.wav')))} WAV files")
print("STATUS:", "PASS (static only; not executed in Godot)" if not errors else "FAIL")
for error in errors:
    print('ERROR:', error)
sys.exit(1 if errors else 0)
