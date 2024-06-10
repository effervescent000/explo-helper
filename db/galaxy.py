from pydantic import BaseModel

from journal_reader.journal_models import DiscoveryScanEvent, FSDJumpEvent, ScanEvent


class Body(BaseModel):
    SystemAddress: int
    BodyID: int


class Star(Body):
    star_class: str


class Planet(Body):
    planet_class: str | None = None
    terraformable: bool = False
    detailed_scan_by_player: bool = False

    def update_from_fss(self, event: ScanEvent) -> None:
        self.planet_class = event.PlanetClass
        self.terraformable = bool(event.TerraformState)
        self.detailed_scan_by_player = True


class System(BaseModel):
    system_name: str
    system_address: int
    star_pos: list[float]

    visited: bool = False
    stars: dict[int, Star] = {}
    planets: dict[int, Planet] = {}
    body_count: int = 0

    def honk(self, event: DiscoveryScanEvent) -> None:
        self.body_count += event.Bodies

    def add_planet_from_scan(self, event: ScanEvent) -> Planet:
        body_id = event.BodyID
        if body_id not in self.planets:
            self.planets[body_id] = Planet(
                SystemAddress=self.system_address,
                BodyID=body_id,
                planet_class=event.PlanetClass,
                terraformable=bool(event.TerraformState),
                detailed_scan_by_player=event.ScanType == "Detailed",
            )
        elif event.ScanType == "Detailed":
            self.planets[body_id].update_from_fss(event)
        return self.planets[body_id]


class Galaxy(BaseModel):
    systems: dict[int, System] = {}
    current_system: System | None = None

    def jump_to_system(self, event: FSDJumpEvent) -> System:
        if event.SystemAddress in self.systems:
            return self.systems[event.SystemAddress]
        system = System(
            **event.dump(),
            visited=True,
        )
        self.systems[system.system_address] = system
        self.current_system = system
        return system
