from shapes import planet_factory
from values import ROCKY


def test_planet_values() -> None:
    rocky_planet = planet_factory(planet_class=ROCKY, terraformable=False)
    assert rocky_planet.values.base == 500
    assert rocky_planet.values.mapped == 1181
