from pydantic import BaseModel

from journal_reader.journal_models import DiscoveryScanEvent, FSDJumpEvent, ScanEvent


class Body(BaseModel):
    SystemAddress: int
    BodyID: int


class Star(Body):
    star_class: str


class Planet(Body):
    PlanetClass: str
    Terraformable: bool = False


class System(BaseModel):
    SystemName: str
    SystemAddress: int
    StarPos: str

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
                SystemAddress=self.SystemAddress,
                BodyID=body_id,
                PlanetClass=event.PlanetClass,  # type: ignore
                Terraformable=bool(event.TerraformState),
            )
        return self.planets[body_id]


class Galaxy(BaseModel):
    systems: dict[int, System] = {}
    current_system: System | None = None

    def jump_to_system(self, event: FSDJumpEvent) -> System:
        if event.SystemAddress in self.systems:
            return self.systems[event.SystemAddress]
        system = System(**event.model_dump(), visited=True)
        self.systems[system.SystemAddress] = system
        return system
