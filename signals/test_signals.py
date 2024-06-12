from db.galaxy import Galaxy
from shapes import planet_factory
from signals.signals import get_possible_bio_signals


def test_get_possible_bio_signals(testing_galaxy: Galaxy) -> None:
    planet = planet_factory(atmosphere="Ammonia", gravity=0.26)
    result = get_possible_bio_signals(planet)
    filtered = [x for x in result if x.genus == "Concha" and x.species == "aureolas"]
    assert len(filtered) == 1
