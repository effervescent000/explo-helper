from shapes import planet_factory
from utils.values import ROCKY


def test_planet_values_mapped() -> None:
    rocky_planet = planet_factory(
        planet_class=ROCKY, terraformable=False, mapped_by_player=True
    )
    assert round(rocky_planet.values_actual.mapped) == 1181
    assert round(rocky_planet.values_actual.bonuses) == 2227


def test_planet_values_unmapped() -> None:
    rocky_planet = planet_factory(
        planet_class=ROCKY, terraformable=False, mapped_by_player=False
    )
    assert rocky_planet.values_actual.base == 500
    assert rocky_planet.values_actual.bonuses == 800


def test_make_bio_signals() -> None:
    planet = planet_factory(atmosphere="Ammonia", gravity=0.26)
    planet.make_possible_bio_signals()
    filtered = [x for x in planet.signals if x.species.genus == "Concha"]
    assert len(filtered) == 1
