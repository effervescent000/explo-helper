from pydantic import BaseModel

from journal_reader.journal_models import (
    DSSSignalEvent,
    DiscoveryScanEvent,
    FSDJumpEvent,
    ScanEvent,
)
from signals.signals import Flora, species
from utils.values import BASE, MEDIAN_MASS, TERRAFORMABLE, PLANET_VALUES, VALUES_ELSE


class BodyValues(BaseModel):
    base: float
    mapped: float
    bonuses: float

    @property
    def total_value(self) -> float:
        if self.mapped != 0:
            return round(self.mapped + self.bonuses)
        return round(self.base + self.bonuses)


class Body(BaseModel):
    SystemAddress: int
    BodyID: int
    BodyName: str

    system_name: str

    @property
    def name(self) -> str:
        return self.BodyName.replace(self.system_name, "").strip()

    @property
    def values_actual(self) -> BodyValues:
        return BodyValues(base=0, mapped=0, bonuses=0)


class Star(Body):
    star_class: str


class BioSignal(BaseModel):
    species: Flora
    genus_found: bool = False
    species_found: bool = False


class Planet(Body):
    planet_class: str | None = None
    terraformable: bool = False
    was_discovered: bool = False
    was_mapped: bool = False
    signal_count: int = 0
    atmosphere: str | None = None
    temperature: float | None = None

    _gravity: float | None = None
    _mass: float | None = None

    detailed_scan_by_player: bool = False
    mapped_by_player: bool = False

    signals: list[BioSignal] = []

    def make_possible_bio_signals(self) -> None:
        species_list = []

        for sp in species:
            if (
                sp.atmosphere_requirement is None
                or len(sp.atmosphere_requirement) == 0
                or self.atmosphere not in sp.atmosphere_requirement
            ):
                continue
            if sp.max_gravity is not None and self.gravity > sp.max_gravity:
                continue
            if (
                sp.max_temperature_k is not None
                and self.temperature is not None
                and self.temperature > sp.max_temperature_k
            ):
                continue
            if (
                sp.min_temperature_k is not None
                and self.temperature is not None
                and self.temperature < sp.min_temperature_k
            ):
                continue

            species_list.append(sp)
        self.signals = [BioSignal(species=x) for x in species_list]

    def update_from_fss(self, event: ScanEvent) -> None:
        self.planet_class = event.PlanetClass
        self.terraformable = bool(event.TerraformState)
        self.detailed_scan_by_player = True
        self._gravity = event.SurfaceGravity
        self._mass = event.MassEM
        self.was_discovered = event.WasDiscovered
        self.was_mapped = event.WasMapped

    def update_signals_from_dss(self, event: DSSSignalEvent) -> None:
        genuses = [x.Genus_Localised for x in event.Genuses]
        for signal in self.signals:
            if signal.species.genus in genuses:
                signal.genus_found = True

    def _calc_values(self, mapped_by_player: bool) -> BodyValues:
        k = PLANET_VALUES.get(self.planet_class or "", VALUES_ELSE).get(BASE, 0)
        if self.terraformable:
            k += PLANET_VALUES.get(self.planet_class or "", VALUES_ELSE).get(
                TERRAFORMABLE, 0
            )

        values = BodyValues(base=0, mapped=0, bonuses=0)

        fss_value = k + (k * self.mass**0.2 * 0.56591828)
        fss_final_value = round(max(fss_value, 500))
        values.base = fss_final_value

        if mapped_by_player:
            mapped_value_baseline = fss_value * 3.3333333333
            values.mapped = mapped_value_baseline

            mapping_first_bonus_multiplier = 3.3333333333
            if self.was_discovered is False:
                mapping_first_bonus_multiplier = 3.699622554
            elif self.was_mapped is False:
                mapping_first_bonus_multiplier = 8.0956

            mapping_bonus_value = (
                fss_value * mapping_first_bonus_multiplier - mapped_value_baseline
            )
            values.bonuses += mapping_bonus_value

        first_discovery_bonus_value = (
            values.total_value * 2.6 - values.total_value
            if self.was_discovered is False
            else 0
        )
        values.bonuses += first_discovery_bonus_value

        return values

    @property
    def gravity(self) -> float:
        return 0 if self._gravity is None else self._gravity / 10

    @property
    def values_actual(self) -> BodyValues:
        return self._calc_values(self.mapped_by_player)

    @property
    def values_estimate(self) -> BodyValues:
        return self._calc_values(mapped_by_player=True)

    @property
    def mass(self) -> float:
        if self._mass is not None:
            return self._mass
        return MEDIAN_MASS.get(self.planet_class or "", {}).get(
            TERRAFORMABLE if self.terraformable else BASE, 0.4
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
                was_discovered=event.WasDiscovered,
                was_mapped=event.WasMapped,
                atmosphere=event.AtmosphereType,
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
