extends SceneTree
## Deterministic money, accuracy and challenge checks without requiring a game window.
const RoundStats = preload("res://scripts/survival_round_stats.gd")
var errors: Array[String] = []
var checks: int = 0

func _initialize() -> void:
    call_deferred("_run")

func check(ok: bool, why: String) -> void:
    checks += 1
    if not ok:
        errors.append(why)
        push_error("SURVIVAL_QA_ERROR: " + why)

func _run() -> void:
    var stats = RoundStats.new()
    stats.begin(1)
    check(stats.active_challenges == ["RAMPAGE", "KILLSTREAK"], "first wave challenge rotation")
    check(stats.accuracy() < 0.0, "no shots must show -- accuracy")
    stats.tick(0.3)
    for i in range(4):
        stats.shot(true, false)
        var reward: int = stats.defeat(i+100, "player", false, i+1, stats.elapsed, 40)
        if i < 3:
            check(reward == 0, "premature rampage payment")
        else:
            check(reward == 500, "four rapid eliminations should pay $500 once")
        stats.tick(0.25)
    check(stats.shots == 4 and stats.hits == 4, "shotgun trigger accounting should be one shot")
    check(stats.defeat(100, "player", false, 1, stats.elapsed, 40) == 0,
        "same enemy death cannot pay money twice")
    check(stats.money_challenges == 500 and stats.kills_player == 4,
        "rampage should be paid once")
    stats.shot(false, false)
    stats.take_hit(12.0)
    check(stats.streak_without_hit == 0 and stats.accuracy() == 80.0,
        "taking any damage resets streak and accuracy is per trigger pull")
    stats.defeat(110, "support", false, 0, stats.elapsed, 40)
    check(stats.kills_support == 1 and stats.kills_player == 4,
        "support kills do not count as player challenge kills")
    var recap: Dictionary = stats.finish(100)
    check(recap["earned_total"] == 4*40 + 40 + 500 + 100,
        "wave report must total paid sources without repaying them")
    check(stats.summary_text().contains("PRECISAO 80%"), "display real accuracy")

    stats.begin(2)
    check(stats.active_challenges == ["KILLSTREAK", "HEADSHOTS"], "second wave rotation")
    for i in range(5):
        stats.tick(0.5)
        var award: int = stats.defeat(200 + i, "player", true, 1+i, stats.elapsed, 50)
        if i == 4:
            check(award == 1000, "five headshots without damage pay two active challenges")
    check(stats.money_challenges == 1000 and stats.headshot_kills == 5,
        "headshot kill count and rewards")
    stats.take_hit(1.0)
    check(stats.streak_without_hit == 0, "armor hit also resets no-damage streak")

    stats.begin(3)
    check(stats.active_challenges == ["HEADSHOTS", "QUAD KILL"], "third wave rotation")
    for i in range(4):
        var earned: int = stats.defeat(300+i, "grenade", false, -50, 1.0, 30)
        if i == 3:
            check(earned == 500, "one explosive event with four kills should pay quadkill")
    check(stats.defeat(400, "grenade", false, -51, 1.0, 30) == 0,
        "a fifth kill from a different explosion must not pay quadkill again")
    check(stats.money_challenges == 500, "quadkill pays only once")
    check(stats.shots == 0 and stats.accuracy() < 0.0, "reset clears previous wave shots")

    stats.begin(6)
    for i in range(10):
        stats.defeat(600+i, "player", false, 60+i, float(i), 50)
    check(stats.money_challenges <= 500, "one reward per active challenge per wave")
    if errors.is_empty():
        print("QA_SURVIVAL_FEATURES_PASS %d assertions" % checks)
        quit(0)
    else:
        print("QA_SURVIVAL_FEATURES_FAIL " + str(errors))
        quit(1)
