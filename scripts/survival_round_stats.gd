extends RefCounted
## One source of truth for the financial/accuracy summary of each Survival wave.
## Tracks actual trigger pulls (one shotgun trigger = one shot).
var wave_number: int = 0
var elapsed: float = 0.0
var shots: int = 0
var hits: int = 0
var kills_player: int = 0
var kills_support: int = 0
var headshot_kills: int = 0
var headshot_hits: int = 0
var damage_taken: float = 0.0
var money_kills: int = 0
var money_challenges: int = 0
var money_headshots: int = 0
var money_spent: int = 0
var money_wave: int = 0
var active_challenges: Array[String] = []
var challenges_awarded: Dictionary = {}
var recent_kills: Array[float] = []
var streak_without_hit: int = 0
var seen_deaths: Dictionary = {}
var achieved: Array[String] = []
var last_result: Dictionary = {}

const CHALLENGE_PAYOUT: int = 500
const CHALLENGES: Array[String] = ["RAMPAGE", "KILLSTREAK", "HEADSHOTS", "QUAD KILL"]
const WINDOW_RAMPAGE: float = 4.0

func begin(number: int) -> void:
    wave_number = number
    elapsed = 0.0
    shots = 0
    hits = 0
    kills_player = 0
    kills_support = 0
    headshot_kills = 0
    headshot_hits = 0
    damage_taken = 0.0
    money_kills = 0
    money_challenges = 0
    money_headshots = 0
    money_spent = 0
    money_wave = 0
    challenges_awarded.clear()
    seen_deaths.clear()
    recent_kills.clear()
    streak_without_hit = 0
    achieved.clear()
    # Deterministic rotation guarantees each wave has achievable objectives
    # and lets QA reproduce rare quadkill/killstreak failures.
    active_challenges = [
        CHALLENGES[(number - 1) % CHALLENGES.size()],
        CHALLENGES[number % CHALLENGES.size()]
    ]

func tick(delta: float) -> void:
    elapsed += maxf(0.0, delta)

func shot(hit_enemy: bool, headshot: bool) -> void:
    shots += 1
    if hit_enemy:
        hits += 1
    if headshot:
        headshot_hits += 1

func take_hit(damage: float) -> void:
    if damage > 0.0:
        damage_taken += damage
        streak_without_hit = 0

func spent(value: int) -> void:
    money_spent += maxi(0, value)

func defeat(enemy_id: int, source: String, headshot: bool, event_id: int, time_seconds: float, bounty: int) -> int:
    if seen_deaths.has(enemy_id):
        return 0
    seen_deaths[enemy_id] = true
    money_kills += bounty
    if source != "player" and source != "melee" and source != "grenade":
        kills_support += 1
        return 0
    kills_player += 1
    streak_without_hit += 1
    recent_kills.append(time_seconds)
    while not recent_kills.is_empty() and time_seconds - recent_kills[0] > WINDOW_RAMPAGE:
        recent_kills.pop_front()
    if headshot:
        headshot_kills += 1
    var earned := 0
    if recent_kills.size() >= 4:
        earned += _award("RAMPAGE")
    if streak_without_hit >= 5:
        earned += _award("KILLSTREAK")
    if headshot_kills >= 5:
        earned += _award("HEADSHOTS")
    # Individual explosion events are counted separately, not four quick kills.
    if source == "grenade" and event_id != 0:
        var explosion_key := "EXP_%d" % event_id
        challenges_awarded[explosion_key] = int(challenges_awarded.get(explosion_key, 0)) + 1
        if int(challenges_awarded[explosion_key]) >= 4:
            earned += _award("QUAD KILL")
    money_challenges += earned
    return earned

func _award(challenge: String) -> int:
    if not active_challenges.has(challenge) or challenges_awarded.get(challenge, false):
        return 0
    challenges_awarded[challenge] = true
    achieved.append(challenge)
    return CHALLENGE_PAYOUT

func accuracy() -> float:
    if shots == 0:
        return -1.0
    return 100.0 * float(hits) / float(shots)

func finish(wave_bonus: int) -> Dictionary:
    # Do not add money_kills/money_challenges again: they were paid on events.
    money_wave = wave_bonus
    last_result = {
        "wave": wave_number, "shots": shots, "hits": hits,
        "accuracy": accuracy(), "kills": kills_player, "support_kills": kills_support,
        "headshots": headshot_kills, "seconds": elapsed,
        "damage": damage_taken, "kills_money": money_kills,
        "challenge_money": money_challenges, "headshot_money": money_headshots,
        "wave_money": money_wave,
        "earned_total": money_kills + money_challenges + money_headshots + money_wave,
        "challenges": achieved.duplicate()
    }
    return last_result.duplicate()

func summary_text() -> String:
    var d := last_result
    if d.is_empty():
        return ""
    var precision := "--" if float(d["accuracy"]) < 0.0 else "%d%%" % roundi(d["accuracy"])
    return "ONDA %02d  /  RELATORIO\nABATES %d   HEADSHOTS %d   PRECISAO %s\nTEMPO %02d:%02d   DANO %.0f\nABATES +$%d  BONUS HS +$%d\nMETAS +$%d  ONDA +$%d  TOTAL +$%d" % [
        int(d["wave"]), int(d["kills"]), int(d["headshots"]), precision,
        int(d["seconds"]) / 60, int(d["seconds"]) % 60, float(d["damage"]),
        int(d["kills_money"]), int(d["headshot_money"]),
        int(d["challenge_money"]), int(d["wave_money"]), int(d["earned_total"])
    ]
