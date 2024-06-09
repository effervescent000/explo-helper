from journal_reader.journal_models import JournalEvent, ScanEvent
from values import BASE, TERRAFORMABLE, VALUES


class Trip:
    def __init__(self) -> None:
        self.bodies_scanned = 0
        self.scanned_value = 0
        self.mapped_value = 0
        self.bonus_value = 0

    def add_entries(self, events: list[JournalEvent]) -> None:
        for event in events:
            if isinstance(event, ScanEvent) and event.ScanType == "Detailed":
                self.bodies_scanned += 1
                self.scanned_value += VALUES.get(event.PlanetClass, {}).get(  # type: ignore
                    TERRAFORMABLE if event.TerraformState else BASE, 0
                )
