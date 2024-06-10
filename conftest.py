import pytest

from db.galaxy import Galaxy, System
from trip_logger.trip import Trip

PRIMARY_SYSTEM_ADDRESS = 12345
PRIMARY_PLANET_ID = 5
PRIMARY_STAR_ID = 1


@pytest.fixture
def testing_galaxy() -> Galaxy:
    system = System(
        system_name="TEST SYSTEM",
        system_address=PRIMARY_SYSTEM_ADDRESS,
        star_pos=[0, 0, 0],
    )
    return Galaxy(systems={PRIMARY_SYSTEM_ADDRESS: system}, current_system=system)


@pytest.fixture
def testing_trip(testing_galaxy: Galaxy) -> Trip:
    return Trip(galaxy=testing_galaxy)
