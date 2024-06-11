BASE = "base"
TERRAFORMABLE = "Terraformable"

HMCB = "High metal content body"
ROCKY = "Rocky body"
ICY = "Icy body"
ROCKY_ICE = "Rocky ice body"
WATER_WORLD = "Water world"
GAS_GIANT_I = "Sudarsky class I gas giant"
GAS_GIANT_II = "Sudarsky class II gas giant"
GAS_GIANT_WITH_WATER = "Gas giant with water based life"

VALUES = {
    GAS_GIANT_I: {BASE: 4_000},
    GAS_GIANT_II: {BASE: 28_000},
    HMCB: {BASE: 9_654, TERRAFORMABLE: 100_677},
    WATER_WORLD: {BASE: 64_831, TERRAFORMABLE: 116_295},
}

VALUES_ELSE = {BASE: 300, TERRAFORMABLE: 93_328}

MEDIAN_MASS = {
    ICY: {BASE: 0.01854},
    ROCKY: {BASE: 0.003359, TERRAFORMABLE: 0.142312},
    ROCKY_ICE: {BASE: 0.180686},
}
