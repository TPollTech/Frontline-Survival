extends RefCounted

const SHOTS = {
    "pistol": preload("res://assets/audio/weapons/pistol.wav"),
    "smg": preload("res://assets/audio/weapons/smg.wav"),
    "rifle": preload("res://assets/audio/weapons/rifle.wav"),
    "shotgun": preload("res://assets/audio/weapons/shotgun.wav"),
    "lmg": preload("res://assets/audio/weapons/lmg.wav"),
}

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
