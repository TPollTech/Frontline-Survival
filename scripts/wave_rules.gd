extends RefCounted
## Frontline Survival's own wave progression rules.
## Inspired by MW3 (2011) Survival's special-threat pacing, not its exact
## map-specific tables. Keeping these rules pure lets CI test 25+ waves quickly.
const MAX_WAVE_ENEMIES: int = 55
const MAX_SIMULTANEOUS: int = 12

static func total_enemies(wave_number: int) -> int:
    if wave_number <= 0:
        return 0
    return mini(5 + wave_number * 2, MAX_WAVE_ENEMIES)

static func heavy_count(wave_number: int) -> int:
    # One announced armored threat at wave 10/15, two from wave 20 onward.
    # No surprise random heavies in ordinary waves, so difficulty is readable.
    if wave_number < 10 or wave_number % 5 != 0:
        return 0
    return 1 if wave_number < 20 else 2

static func kind_for_spawn(wave_number: int, remaining_in_queue: int, roll: float) -> String:
    if remaining_in_queue <= 0 or wave_number <= 0:
        return "none"
    if remaining_in_queue <= heavy_count(wave_number):
        return "heavy"
    if wave_number >= 7 and roll > 0.75:
        return "runner"
    return "soldier"

static func is_armored_wave(wave_number: int) -> bool:
    return heavy_count(wave_number) > 0

static func wave_alert(wave_number: int) -> String:
    if not is_armored_wave(wave_number):
        return ""
    var count: int = heavy_count(wave_number)
    return "ALERTA: %d UNIDADE%s BLINDADA%s NA ONDA!" % [
        count, "" if count == 1 else "S", "" if count == 1 else "S"
    ]
