extends SceneTree
## Fast, deterministic regression for the composition of 50 Survival waves.
## This is a data/scheduling simulation, NOT a claim of 50 played waves.
const WaveRules = preload("res://scripts/wave_rules.gd")
var failures: Array[String] = []
var assertions: int = 0

func _initialize() -> void:
    call_deferred("_check_rules")

func expect(condition: bool, message: String) -> void:
    assertions += 1
    if not condition:
        failures.append(message)
        push_error("WAVE_RULE_ERROR: " + message)

func _check_rules() -> void:
    expect(WaveRules.total_enemies(0) == 0, "wave zero must be empty")
    expect(WaveRules.total_enemies(1) == 7, "wave 1 expected seven enemies")
    expect(WaveRules.total_enemies(10) == 25, "wave 10 expected 25 enemies")
    expect(WaveRules.total_enemies(25) == 55, "wave 25 is capped at 55")
    expect(WaveRules.total_enemies(200) == 55, "infinite game has capped batch size")
    expect(WaveRules.heavy_count(9) == 0, "no surprise heavy on wave 9")
    expect(WaveRules.heavy_count(10) == 1, "one heavy at first milestone")
    expect(WaveRules.heavy_count(15) == 1, "one heavy with escort at wave 15")
    expect(WaveRules.heavy_count(20) == 2, "two heavies on wave 20")
    expect(WaveRules.heavy_count(21) == 0, "no unannounced heavy on wave 21")
    expect(WaveRules.kind_for_spawn(0, 2, 0.5) == "none", "invalid wave guard")
    expect(WaveRules.kind_for_spawn(1, 0, 0.5) == "none", "empty queue guard")
    expect(WaveRules.kind_for_spawn(6, 2, 0.99) == "soldier", "runners unlock at wave 7")
    expect(WaveRules.kind_for_spawn(7, 2, 0.99) == "runner", "wave 7 runner variety")
    expect(WaveRules.wave_alert(9) == "", "ordinary wave must be silent")
    expect(WaveRules.wave_alert(10).contains("BLINDADA"), "visual special-wave warning missing")

    var total_simulated: int = 0
    var heavies_simulated: int = 0
    for wave_number in range(1, 51):
        var number: int = WaveRules.total_enemies(wave_number)
        expect(number > 0 and number <= 55, "batch limit at wave %d" % wave_number)
        var heavy_total := 0
        var soldier_total := 0
        for remaining in range(number, 0, -1):
            var kind: String = WaveRules.kind_for_spawn(wave_number, remaining, 0.2)
            expect(kind == "heavy" or kind == "soldier", "unknown normal composition at %d" % wave_number)
            if kind == "heavy":
                heavy_total += 1
            else:
                soldier_total += 1
        expect(heavy_total == WaveRules.heavy_count(wave_number),
            "heavy budget mismatch at wave %d" % wave_number)
        expect(heavy_total + soldier_total == number, "lost enemy from spawn queue at %d" % wave_number)
        expect(WaveRules.is_armored_wave(wave_number) == (heavy_total > 0),
            "special wave label disagrees with threats at %d" % wave_number)
        expect((WaveRules.wave_alert(wave_number) != "") == (heavy_total > 0),
            "heavy wave must have a visual warning at %d" % wave_number)
        total_simulated += number
        heavies_simulated += heavy_total
    if failures.is_empty():
        print("QA_WAVE_RULES_PASS %d assertions, 50 compositions, %d planned enemies, %d milestone heavies" % [
            assertions, total_simulated, heavies_simulated
        ])
        quit(0)
    else:
        print("QA_WAVE_RULES_FAIL: " + str(failures))
        quit(1)
