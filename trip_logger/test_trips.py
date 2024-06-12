from conftest import PRIMARY_PLANET_ID
from shapes import scan_event_factory
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
