extends RefCounted
## Gentle original two-part low percussion for wave completion.
## No high-frequency UI chirps, samples or background music.
## Synthesized once on startup; independent of platform WAV imports.
static func create(parent: Node) -> AudioStreamPlayer:
    var rate: int = 22050
    var duration: float = 0.50
    var count: int = int(float(rate) * duration)
    var pcm := PackedByteArray()
    pcm.resize(count * 2)
    for i in range(count):
        var t: float = float(i) / float(rate)
        var second: float = maxf(0.0, t - 0.19)
        var first_env: float = exp(-t * 19.0)
        var second_env: float = exp(-second * 22.0) if t >= 0.19 else 0.0
        # Sub-bass thuds, intentionally no 1kHz+ beeps.
        var bass: float = sin(TAU * (82.0 - t * 22.0) * t) * first_env * 0.29
        bass += sin(TAU * (69.0 - second * 18.0) * second) * second_env * 0.17
        var sample: int = clampi(int(bass * 32760.0), -32760, 32760)
        pcm.encode_s16(i * 2, sample)
    var clip := AudioStreamWAV.new()
    clip.format = AudioStreamWAV.FORMAT_16_BITS
    clip.mix_rate = rate
    clip.stereo = false
    clip.data = pcm
    var audio := AudioStreamPlayer.new()
    audio.stream = clip
    audio.volume_db = -13.0
    audio.bus = "UI"
    parent.add_child(audio)
    return audio
