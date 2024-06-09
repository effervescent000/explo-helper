from journal_reader.journal_models import JournalEvent, ScanEvent


class Trip:
    def __init__(self) -> None:
        self.bodies_scanned = 0

    def add_entries(self, events: list[JournalEvent]) -> None:
        for event in events:
            if isinstance(event, ScanEvent) and event.ScanType == "Detailed":
                self.bodies_scanned += 1
