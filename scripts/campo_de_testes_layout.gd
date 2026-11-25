extends RefCounted
## Canonical placement recipe for the existing Campo de Testes.
## Metres, Godot +Y up. The production assembler owns geometry, materials,
## child insertion order, physics, gameplay, LOD and random variation.
## These placements are not a separate Studio preview model.

const GROUND := [Vector3(0, -0.5, 0), Vector3(52, 1, 52), Color(0.83, 0.87, 0.83)]
const WALLS := [
    [Vector3(0, 2.2, -26), Vector3(52, 4.4, 1), Color(0.33, 0.37, 0.41)],
    [Vector3(0, 2.2, 26), Vector3(52, 4.4, 1), Color(0.34, 0.37, 0.40)],
    [Vector3(-26, 2.2, 0), Vector3(1, 4.4, 52), Color(0.35, 0.39, 0.41)],
    [Vector3(26, 2.2, 0), Vector3(1, 4.4, 52), Color(0.34, 0.37, 0.39)],
]

const CONTAINERS := [
    [Vector3(-9, 1.20, -6), Vector3(5.2, 2.4, 2.0), Color(0.33, 0.40, 0.33)],
    [Vector3(9, 1.00, 6), Vector3(5.5, 2.0, 2.0), Color(0.47, 0.34, 0.24)],
    [Vector3(-9, 1.10, 8), Vector3(2.2, 2.2, 4.3), Color(0.26, 0.39, 0.42)],
    [Vector3(10, 0.80, -9), Vector3(2.5, 1.6, 4.0), Color(0.32, 0.36, 0.33)],
]

const BARRICADES := [
    [Vector3(-2, 0.0, -13), 4, 2],
    [Vector3(2, 0.0, 13), 4, 2],
    [Vector3(-15, 0.0, 1), 3, 2],
    [Vector3(16, 0.0, -1), 3, 2],
]

const SHOPS := [
    ["weapons", "ARMAS", Vector3(-19, 0, -19), Color(0.83, 0.30, 0.22)],
    ["gear", "EQUIPAMENTOS", Vector3(19, 0, -19), Color(0.24, 0.67, 0.36)],
    ["support", "SUPORTE", Vector3(0, 0, 21), Color(0.22, 0.62, 0.84)],
]

const BARREL_CENTERS := [Vector3(-18, 0, -8), Vector3(18, 0, 10), Vector3(-5, 0, 18), Vector3(15, 0, -19)]
const BARREL_OFFSET := Vector3(0.83, 0, 0.25)
const BARREL_FIRST_COLOR := Color(0.31, 0.44, 0.46)
const BARREL_SECOND_COLOR := Color(0.43, 0.34, 0.25)
const LIGHT_X := [-23.0, 23.0]
const LIGHT_Z := [-23.0, 23.0]
const SIGN_POSITION := Vector3(0, 3.45, -25.1)

static func decorative_boxes() -> Array:
    var boxes: Array = []
    # Linhas de pista e faixas de seguranca no patio.
    var paint := Color(0.72, 0.68, 0.47)
    for i in range(8):
        boxes.append([Vector3(-13 + float(i) * 3.5, 0.02, -16.7), Vector3(1.5, 0.025, 0.11), paint])
    boxes.append([Vector3(0, 0.015, -2.2), Vector3(0.10, 0.022, 29.0), Color(0.64, 0.64, 0.53)])
    # Fachadas do complexo no limite do mapa.
    for x in [-18.0, 0.0, 18.0]:
        boxes.append([Vector3(x, 2.3, -25.4), Vector3(7.5, 3.7, 0.18), Color(0.21, 0.26, 0.30)])
        boxes.append([Vector3(x, 4.3, -25.0), Vector3(8.0, 0.12, 1.6), Color(0.13, 0.16, 0.18)])
        boxes.append([Vector3(x, 3.7, -25.25), Vector3(6.4, 0.14, 0.20), Color(0.57, 0.51, 0.31)])
        for j in range(5):
            boxes.append([Vector3(x - 2.7 + float(j) * 1.35, 2.2, -25.29), Vector3(0.045, 3.0, 0.04), Color(0.33, 0.40, 0.43)])
    return boxes
