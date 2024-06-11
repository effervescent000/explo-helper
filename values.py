DSS_MULTIPLIER = 4.16
FD_MULTIPLIER = 2.6

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
    GAS_GIANT_WITH_WATER: {BASE: 900},
    HMCB: {BASE: 14_000, TERRAFORMABLE: 164_000},
    ICY: {BASE: 500},
    ROCKY: {BASE: 500, TERRAFORMABLE: 130_000},
    ROCKY_ICE: {BASE: 500},
    WATER_WORLD: {BASE: 100_000, TERRAFORMABLE: 269_000},
}
