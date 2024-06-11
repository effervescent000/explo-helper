from shapes import planet_factory
from values import ROCKY


def test_planet_values_mapped() -> None:
    rocky_planet = planet_factory(
        planet_class=ROCKY, terraformable=False, mapped_by_player=True
    )
    assert round(rocky_planet.values.mapped) == 1181
    assert round(rocky_planet.values.bonuses) == 2227


def test_planet_values_unmapped() -> None:
    rocky_planet = planet_factory(
        planet_class=ROCKY, terraformable=False, mapped_by_player=False
    )
    assert rocky_planet.values.base == 500
    assert rocky_planet.values.bonuses == 800
