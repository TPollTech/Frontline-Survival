extends RefCounted

const SHOTS = {
    "pistol": preload("res://assets/audio/weapons/pistol.wav"),
    "smg": preload("res://assets/audio/weapons/smg.wav"),
    "rifle": preload("res://assets/audio/weapons/rifle.wav"),
    "shotgun": preload("res://assets/audio/weapons/shotgun.wav"),
    "lmg": preload("res://assets/audio/weapons/lmg.wav"),
}

const RELOADS = {
    "pistol": preload("res://assets/audio/reloads/pistol.wav"),
    "smg": preload("res://assets/audio/reloads/smg.wav"),
    "rifle": preload("res://assets/audio/reloads/rifle.wav"),
    "shotgun": preload("res://assets/audio/reloads/shotgun.wav"),
    "lmg": preload("res://assets/audio/reloads/lmg.wav"),
}

static func reload_for(weapon_id: String) -> AudioStreamWAV:
    return RELOADS.get(weapon_id) as AudioStreamWAV

static func shot_for(weapon_id: String) -> AudioStreamWAV:
    return SHOTS.get(weapon_id, SHOTS["rifle"]) as AudioStreamWAV

static func add_spatial_shot(muzzle: Node3D, weapon_id: String) -> AudioStreamPlayer3D:
    var audio := AudioStreamPlayer3D.new()
    audio.stream = shot_for(weapon_id)
    audio.bus = "SFX"
    audio.volume_db = -11.0
    audio.unit_size = 8.0
    audio.max_distance = 45.0
    audio.max_polyphony = 2
    muzzle.add_child(audio)
    return audio
