from typing import Callable, Sequence
from db.galaxy import Galaxy, Planet, System
from journal_reader.journal_models import (
    DSSEvent,
    DSSSignalEvent,
    FSDJumpEvent,
    FSSSignalEvent,
    JournalEvent,
    ScanEvent,
)


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
    def __init__(
        self,
        galaxy: Galaxy,
        refresh_func: Callable[[], None],
        add_body_to_ui: Callable[[Planet], None],
        clear_system: Callable[[], None],
    ) -> None:
        self.galaxy = galaxy

        self.refresh = refresh_func
        self.add_body_to_ui = add_body_to_ui
        self.clear_system = clear_system
        self.bodies_scanned: list[Planet] = []
        self.bodies_mapped: list[Planet] = []

    @property
    def bodies_scanned_count(self) -> int:
        return len(self.bodies_scanned)

    @property
    def bodies_scanned_value(self) -> int:
        return round(
            sum(x.cartographic_values_actual.base for x in self.bodies_scanned)
        )

    @property
    def bodies_mapped_count(self) -> int:
        return len(self.bodies_mapped)

    @property
    def bodies_mapped_value(self) -> int:
        return round(
            sum(x.cartographic_values_actual.mapped for x in self.bodies_mapped)
        )

    @property
    def bonuses(self) -> int:
        return round(
            sum(x.cartographic_values_actual.bonuses for x in self.bodies_scanned)
        )

    def add_entries(self, events: Sequence[JournalEvent]) -> None:
        for event in events:
            if isinstance(event, FSDJumpEvent):
                self.galaxy.jump_to_system(event)
                self.clear_system()
                continue

            if (
                isinstance(event, ScanEvent)
                and event.ScanType == "Detailed"
                and event.PlanetClass is not None
            ):
                if self.galaxy.current_system:
                    new_scan = is_new_scan(self.galaxy.current_system, event)
                    planet = self.galaxy.current_system.add_planet_from_scan(event)
                    if new_scan is True:
                        self.bodies_scanned.append(planet)
                        self.add_body_to_ui(planet)
                    else:
                        planet.update_from_fss(event)
                continue

            if isinstance(event, DSSEvent):
                if self.galaxy.current_system is not None:
                    planet = self.galaxy.current_system.planets.get(event.BodyID, None)
                    if planet is not None:
                        planet.mapped_by_player = True
                        self.bodies_mapped.append(planet)
                continue

            if isinstance(event, FSSSignalEvent):
                if self.galaxy.current_system is not None:
                    self.galaxy.current_system.add_planet_from_signals(event)
                continue

            if isinstance(event, DSSSignalEvent):
                if self.galaxy.current_system is not None:
                    planet = self.galaxy.current_system.planets.get(event.BodyID, None)
                    if planet is not None:
                        planet.update_signals_from_dss(event)
                continue

        self.refresh()
