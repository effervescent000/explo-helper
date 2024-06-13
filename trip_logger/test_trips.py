from typing import cast
from conftest import PRIMARY_PLANET_ID
from db.galaxy import System
from shapes import fss_signal_event_factory, scan_event_factory, signal_count_factory
from trip_logger.trip import Trip


def test_trip_add_entries_fss_scan(testing_trip: Trip) -> None:
    """If receiving multiple detailed scans of the same body, only add its value once."""
    events = [
        scan_event_factory(BodyID=PRIMARY_PLANET_ID),
        scan_event_factory(BodyID=PRIMARY_PLANET_ID),
    ]
    assert testing_trip.bodies_scanned_value == 0

    testing_trip.add_entries(events)

    assert testing_trip.bodies_scanned_value == 500
    assert testing_trip.bodies_scanned_count == 1


def test_trip_add_entries_autoscan_then_fss(testing_trip: Trip) -> None:
    """If receiving an autoscan followed by a detailed scan, only add its value once."""
    events = [
        scan_event_factory(BodyID=PRIMARY_PLANET_ID, ScanType="AutoScan"),
        scan_event_factory(BodyID=PRIMARY_PLANET_ID),
    ]
    assert testing_trip.bodies_scanned_value == 0

    testing_trip.add_entries(events)

    assert testing_trip.bodies_scanned_value == 500
    assert testing_trip.bodies_scanned_count == 1


def test_fss_adds_all_params(testing_trip: Trip) -> None:
    event = scan_event_factory(
        BodyID=PRIMARY_PLANET_ID, MassEM=0.25, BodyName="TESTING"
    )
    testing_trip.add_entries([event])

    assert testing_trip.bodies_scanned[0].mass == 0.25


def test_add_biosignals(testing_trip: Trip) -> None:
    events = [
        fss_signal_event_factory(Signals=[signal_count_factory(Count=2)]),
        scan_event_factory(BodyID=PRIMARY_PLANET_ID),
    ]
    testing_trip.add_entries(events)

    current_system = cast(System, testing_trip.galaxy.current_system)
    assert len(current_system.planets) == 1

    planet = current_system.planets[PRIMARY_PLANET_ID]
    assert planet.signal_count == 2


def test_make_bio_signals_from_start(testing_trip: Trip) -> None:
    """Test making bio signals without a premade planet."""
    events = [
        fss_signal_event_factory(Signals=[signal_count_factory(Count=2)]),
        scan_event_factory(BodyID=PRIMARY_PLANET_ID, AtmosphereType="Ammonia"),
    ]
    testing_trip.add_entries(events)

    current_system = cast(System, testing_trip.galaxy.current_system)
    planet = current_system.planets[PRIMARY_PLANET_ID]
    assert len(planet.signals) > 0
