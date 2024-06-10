from db.galaxy import Galaxy
from journal_reader.journal_models import (
    DSSEvent,
    FSDJumpEvent,
    JournalEvent,
    ScanEvent,
)
from values import BASE, TERRAFORMABLE, VALUES


class Trip:
    def __init__(self, galaxy: Galaxy) -> None:
        self.galaxy = galaxy

        self.bodies_scanned = 0
        self.bodies_mapped = 0

        self.scanned_value = 0
        self.mapped_value = 0
        self.bonus_value = 0

    def add_entries(self, events: list[JournalEvent]) -> None:
        for event in events:
            if isinstance(event, FSDJumpEvent):
                system = self.galaxy.jump_to_system(event)
                self.galaxy.current_system = system
                continue
            if isinstance(event, ScanEvent) and event.ScanType == "Detailed":
                if self.galaxy.current_system:
                    self.galaxy.current_system.add_planet_from_scan(event)
                self.bodies_scanned += 1
                self.scanned_value += VALUES.get(event.PlanetClass, {}).get(  # type: ignore
                    TERRAFORMABLE if event.TerraformState else BASE, 0
                )
                continue

            if isinstance(event, DSSEvent):
                self.bodies_mapped += 1
