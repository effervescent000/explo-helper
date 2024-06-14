from typing import cast
from pydantic import BaseModel

from journal_reader.journal_models import (
    DSSSignalEvent,
    DiscoveryScanEvent,
    FSDJumpEvent,
    FSSSignalEvent,
    ScanEvent,
)
from signals.signals import Flora, species_list
from utils.values import BASE, MEDIAN_MASS, TERRAFORMABLE, PLANET_VALUES, VALUES_ELSE


def get_bio_signal_values_from_list(
    sorted_list: list["BioSignal"], count: int
) -> list["BioSignal"]:
    signals_to_value: list[BioSignal] = []
    i = 0
    while i < len(sorted_list) and len(signals_to_value) < count:
        genuses_found = set(x.species.genus for x in signals_to_value)
        signal = sorted_list[i]
        if signal.species.genus not in genuses_found:
            signals_to_value.append(signal)
        i += 1
    return signals_to_value


class BodyBioValues(BaseModel):
    min: float
    max: float
    actual: float = 0
    bonuses: float


class BodyCartographicValues(BaseModel):
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
    BodyName: str = ""

    system_name: str = ""

    @property
    def name(self) -> str:
        return self.BodyName.replace(self.system_name, "").strip()

    @property
    def cartographic_values_actual(self) -> BodyCartographicValues:
        return BodyCartographicValues(base=0, mapped=0, bonuses=0)


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

    surface_gravity: float | None = None
    mass_em: float | None = None

    detailed_scan_by_player: bool = False
    mapped_by_player: bool = False

    signals: list[BioSignal] = []

    def make_possible_bio_signals(self) -> None:
        maybe_species_list = []

        for sp in species_list:
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

            maybe_species_list.append(sp)
        self.signals = [BioSignal(species=x) for x in maybe_species_list]

    def update_from_fss(self, event: ScanEvent) -> None:
        self.BodyName = event.BodyName
        self.system_name = event.StarSystem
        self.planet_class = event.PlanetClass
        self.terraformable = bool(event.TerraformState)
        self.detailed_scan_by_player = True
        self.surface_gravity = event.SurfaceGravity
        self.mass_em = event.MassEM
        self.atmosphere = event.AtmosphereType
        self.was_discovered = event.WasDiscovered
        self.was_mapped = event.WasMapped

    def update_signals_from_dss(self, event: DSSSignalEvent) -> None:
        genuses = [x.Genus_Localised for x in event.Genuses]
        for signal in self.signals:
            if signal.species.genus in genuses:
                signal.genus_found = True

    @property
    def bio_signal_values(self) -> BodyBioValues:
        if self.signal_count < 1:
            return BodyBioValues(min=0, max=0, actual=0, bonuses=0)
        min_sorted = sorted(self.signals, key=lambda x: str(x.species.value))
        signals_to_value_min = get_bio_signal_values_from_list(
            min_sorted, self.signal_count
        )

        max_sorted = sorted(
            self.signals, key=lambda x: str(x.species.value), reverse=True
        )
        signals_to_value_max = get_bio_signal_values_from_list(
            max_sorted, self.signal_count
        )

        values = BodyBioValues(
            min=sum(cast(int, x.species.value) for x in signals_to_value_min),
            max=sum(cast(int, x.species.value) for x in signals_to_value_max),
            actual=0,
            bonuses=0,
        )

        return values

    def _calc_values(self, mapped_by_player: bool) -> BodyCartographicValues:
        k = PLANET_VALUES.get(self.planet_class or "", VALUES_ELSE).get(BASE, 0)
        if self.terraformable:
            k += PLANET_VALUES.get(self.planet_class or "", VALUES_ELSE).get(
                TERRAFORMABLE, 0
            )

        values = BodyCartographicValues(base=0, mapped=0, bonuses=0)

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
        return 0 if self.surface_gravity is None else self.surface_gravity / 10

    @property
    def cartographic_values_actual(self) -> BodyCartographicValues:
        return self._calc_values(self.mapped_by_player)

    @property
    def cartographic_values_estimate(self) -> BodyCartographicValues:
        return self._calc_values(mapped_by_player=True)

    @property
    def mass(self) -> float:
        if self.mass_em is not None:
            return self.mass_em
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
                mass_em=event.MassEM,
                surface_gravity=event.SurfaceGravity,
                was_discovered=event.WasDiscovered,
                was_mapped=event.WasMapped,
                atmosphere=event.AtmosphereType,
            )
        elif event.ScanType == "Detailed":
            self.planets[body_id].update_from_fss(event)
        if self.planets[body_id].signal_count > 0:
            self.planets[body_id].make_possible_bio_signals()
        return self.planets[body_id]

    def add_planet_from_signals(self, event: FSSSignalEvent) -> Planet:
        body_id = event.BodyID
        biosignals = [x for x in event.Signals if x.Type_Localised == "Biological"]
        if body_id not in self.planets:
            self.planets[body_id] = Planet(
                SystemAddress=self.system_address,
                BodyID=body_id,
                signal_count=sum(x.Count for x in biosignals),
            )
        else:
            self.planets[body_id].signal_count = sum(x.Count for x in biosignals)
        return self.planets[body_id]


class Galaxy(BaseModel):
    systems: dict[int, System] = {
        -1: System(
            system_address=-1, system_name="Oops you broke it :(", star_pos=[0, 0, 0]
        )
    }
    current_system_id: int = -1

    def jump_to_system(self, event: FSDJumpEvent) -> System:
        if event.SystemAddress in self.systems:
            system = self.systems[event.SystemAddress]
            system.visited = True
            return system
        system = System(
            **event.dump(),
            visited=True,
        )
        self.systems[system.system_address] = system
        self.current_system_id = system.system_address
        return system

    @property
    def current_system(self) -> System:
        return self.systems[self.current_system_id]
