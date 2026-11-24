extends RefCounted
## Distance-only runtime selector. Keeps collision outside of the visual swap.
var distances: Array[float] = []
var hysteresis: float
var current: int = -1

func configure(starts: Array[float], margin: float) -> bool:
    if starts.size() != 3 or starts[0] != 0.0 or not is_finite(margin) or margin < 0.0:
        return false
    for i in range(1, starts.size()):
        if not is_finite(starts[i]) or starts[i]-starts[i-1] <= 2.0*margin:
            return false
    distances = starts.duplicate()
    hysteresis = margin
    current = -1
    return true

func select(distance: float) -> int:
    if distances.size() != 3 or not is_finite(distance) or distance < 0.0:
        return -1
    if current == -1:
        current = 0
        for i in range(1,distances.size()):
            if distance >= distances[i]:
                current = i
    else:
        while current < distances.size()-1 and distance >= distances[current+1]+hysteresis:
            current += 1
        while current > 0 and distance < distances[current]-hysteresis:
            current -= 1
    return current

func update_visual(visual: MeshInstance3D, levels: Array[ArrayMesh], distance: float) -> bool:
    if visual == null or levels.size() != 3 or levels.has(null):
        return false
    var index := select(distance)
    if index < 0:
        return false
    if visual.mesh != levels[index]:
        visual.mesh = levels[index]
    return true
