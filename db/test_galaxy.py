from shapes import bio_signal_factory, planet_factory
from utils.values import ROCKY
from signals.signals import species_list


def test_planet_values_mapped() -> None:
    rocky_planet = planet_factory(
        planet_class=ROCKY, terraformable=False, mapped_by_player=True
    )
    assert round(rocky_planet.cartographic_values_actual.mapped) == 1181
    assert round(rocky_planet.cartographic_values_actual.bonuses) == 2227


def test_planet_values_unmapped() -> None:
    rocky_planet = planet_factory(
        planet_class=ROCKY, terraformable=False, mapped_by_player=False
    )
    assert rocky_planet.cartographic_values_actual.base == 500
    assert rocky_planet.cartographic_values_actual.bonuses == 800


def test_planet_values_already_discovered_mapped() -> None:
    rocky_planet = planet_factory(
        planet_class=ROCKY,
        terraformable=False,
        was_discovered=True,
        was_mapped=True,
        mapped_by_player=True,
    )
    assert round(rocky_planet.cartographic_values_actual.mapped) == 1181
    assert rocky_planet.cartographic_values_actual.bonuses == 0


def test_make_bio_signals() -> None:
    planet = planet_factory(atmosphere="Ammonia", gravity=0.26)
    planet.make_possible_bio_signals()
    filtered = [x for x in planet.signals if x.species.genus == "Concha"]
    assert len(filtered) == 1


def test_make_bio_values() -> None:
    planet = planet_factory(
        signal_count=1,
        signals=[
            bio_signal_factory(
                species=[
                    x
                    for x in species_list
                    if x.genus == "Bacterium" and x.species == "nebulus"
                ][0]
            ),
            bio_signal_factory(
                species=[
                    x
                    for x in species_list
                    if x.genus == "Concha" and x.species == "aureolas"
                ][0]
            ),
        ],
    )

    values = planet.bio_signal_values

    assert values.min == 5_289_900
    assert values.max == 7_774_700
    assert values.actual == 0
    assert values.bonuses == 0
