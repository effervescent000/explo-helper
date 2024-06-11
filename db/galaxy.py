from pydantic import BaseModel

from journal_reader.journal_models import DiscoveryScanEvent, FSDJumpEvent, ScanEvent
from values import BASE, DSS_MULTIPLIER, TERRAFORMABLE, VALUES


class BodyValues(BaseModel):
    base: int
    mapped: int
    bonuses: int


class Body(BaseModel):
    SystemAddress: int
    BodyID: int
    BodyName: str

    system_name: str

    @property
    def name(self) -> str:
        return self.BodyName.replace(self.system_name, "").strip()


class Star(Body):
    star_class: str


class Planet(Body):
    planet_class: str | None = None
    terraformable: bool = False
    detailed_scan_by_player: bool = False
    discovered: bool = False

    def update_from_fss(self, event: ScanEvent) -> None:
        self.planet_class = event.PlanetClass
        self.terraformable = bool(event.TerraformState)
        self.detailed_scan_by_player = True
        self.discovered = event.WasDiscovered

    @property
    def values(self) -> BodyValues:
        fss_value = VALUES.get(self.planet_class or "", {}).get(
            TERRAFORMABLE if self.terraformable else BASE, 0
        )
        return BodyValues(
            base=fss_value,
            mapped=round(fss_value * DSS_MULTIPLIER - fss_value),
            bonuses=0,
        )


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
                BodyName=event.BodyName,
                BodyID=body_id,
                planet_class=event.PlanetClass,
                terraformable=bool(event.TerraformState),
                detailed_scan_by_player=event.ScanType == "Detailed",
                system_name=event.StarSystem,
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
