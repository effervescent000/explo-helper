from typing import Sequence
from db.galaxy import Galaxy, System
from journal_reader.journal_models import (
    DSSEvent,
    FSDJumpEvent,
    JournalEvent,
    ScanEvent,
)
from values import BASE, DSS_MULTIPLIER, TERRAFORMABLE, VALUES


def is_new_scan(system: System, event: ScanEvent) -> bool:
    if event.ScanType != "Detailed":
        return False
    body = system.planets.get(event.BodyID, None)
    if body is None:
        return True
    if not body.detailed_scan_by_player:
        return True
    return False


class Trip:
    def __init__(self, galaxy: Galaxy) -> None:
        self.galaxy = galaxy

        self.bodies_scanned = 0
        self.bodies_mapped = 0

        self.scanned_value = 0
        self.mapped_value = 0
        self.bonus_value = 0

    def add_entries(self, events: Sequence[JournalEvent]) -> None:
        for event in events:
            if isinstance(event, FSDJumpEvent):
                self.galaxy.jump_to_system(event)
                continue
            if (
                isinstance(event, ScanEvent)
                and event.ScanType == "Detailed"
                and event.PlanetClass is not None
            ):
                if self.galaxy.current_system:
                    if is_new_scan(self.galaxy.current_system, event) is True:
                        self.bodies_scanned += 1
                        self.scanned_value += VALUES.get(
                            event.PlanetClass or "", {}
                        ).get(TERRAFORMABLE if bool(event.TerraformState) else BASE, 0)
                    self.galaxy.current_system.add_planet_from_scan(event)
                continue

            if isinstance(event, DSSEvent):
                self.bodies_mapped += 1
                value = 0
                if self.galaxy.current_system is not None:
                    planet = self.galaxy.current_system.planets.get(event.BodyID, None)
                    if planet is not None:
                        value = planet.values.mapped
                self.mapped_value += value
