import pytest

from db.galaxy import Galaxy, Planet, System
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
    planet = Planet(
        BodyID=PRIMARY_PLANET_ID,
        SystemAddress=PRIMARY_SYSTEM_ADDRESS,
        BodyName="stupid testing planet",
        system_name="TEST SYSTEM",
    )
    system.planets[PRIMARY_PLANET_ID] = planet
    return Galaxy(
        systems={PRIMARY_SYSTEM_ADDRESS: system},
        current_system_id=system.system_address,
    )


@pytest.fixture
def testing_trip(testing_galaxy: Galaxy) -> Trip:
    return Trip(
        galaxy=testing_galaxy,
        refresh_func=lambda *args: None,
        add_body_to_ui=lambda *args: None,
        clear_system=lambda *args: None,
    )
