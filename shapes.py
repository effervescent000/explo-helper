from typing import Literal
from conftest import PRIMARY_PLANET_ID, PRIMARY_SYSTEM_ADDRESS
from db.galaxy import BioSignal, Planet
from journal_reader.journal_models import (
    EventType,
    FSSSignalEvent,
    GenericSignal,
    JournalEvent,
    ScanEvent,
)
from signals.signals import Flora, species_list
from utils.values import ROCKY


def event_factory(*, timestamp: str | None = None, event: EventType) -> JournalEvent:
    return JournalEvent(timestamp=timestamp or "2024-06-09T00:55:18Z", event=event)


def scan_event_factory(
    *,
    StarSystem: str | None = None,
    SystemAddress: int | None = None,
    ScanType: Literal["AutoScan"]
    | Literal["Detailed"]
    | Literal["Basic"]
    | None = None,
    BodyName: str | None = None,
    BodyID: int | None = None,
    PlanetClass: str | None = None,
    TerraformState: str | None = None,
    MassEM: float | None = None,
    SurfaceGravity: float | None = None,
    AtmosphereType: str | None = None,
    WasDiscovered: bool = False,
    WasMapped: bool = False,
) -> ScanEvent:
    return ScanEvent(
        **event_factory(event="Scan").model_dump(),
        StarSystem=StarSystem or "DONT CARE",
        SystemAddress=SystemAddress or PRIMARY_SYSTEM_ADDRESS,
        ScanType=ScanType or "Detailed",
        BodyName=BodyName or "DOESNT MATTER",
        BodyID=BodyID or PRIMARY_PLANET_ID,
        PlanetClass=PlanetClass or ROCKY,
        TerraformState=TerraformState or "",
        MassEM=MassEM,
        SurfaceGravity=SurfaceGravity,
        AtmosphereType=AtmosphereType,
        WasDiscovered=WasDiscovered or False,
        WasMapped=WasMapped or False,
    )


def signal_count_factory(
    *,
    Type: str | None = None,
    Type_Localised: str | None = None,
    Count: int | None = None,
) -> GenericSignal:
    return GenericSignal(
        Type=Type or "$SAA_SignalType_Biological;",
        Type_Localised=Type_Localised or "Biological",
        Count=Count if Count is not None else 0,
    )


def fss_signal_event_factory(
    *,
    BodyID: int | None = None,
    SystemAddress: int | None = None,
    Signals: list[GenericSignal],
) -> FSSSignalEvent:
    return FSSSignalEvent(
        **event_factory(event="FSSBodySignals").model_dump(),
        BodyID=BodyID or PRIMARY_PLANET_ID,
        SystemAddress=SystemAddress or PRIMARY_SYSTEM_ADDRESS,
        Signals=Signals,
    )


def bio_signal_factory(
    *,
    species: Flora | None = None,
    genus_found: bool = False,
    species_found: bool = False,
) -> BioSignal:
    return BioSignal(
        species=species or species_list[0],
        genus_found=genus_found,
        species_found=species_found,
    )


def planet_factory(
    *,
    StarSystem: str | None = None,
    SystemAddress: int | None = None,
    BodyName: str | None = None,
    BodyID: int | None = None,
    planet_class: str | None = None,
    terraformable: bool = False,
    detailed_scan_by_player: bool = False,
    was_discovered: bool = False,
    was_mapped: bool = False,
    mapped_by_player: bool = False,
    atmosphere: str | None = None,
    gravity: float | None = None,
    mass: float | None = None,
    signal_count: int | None = None,
    signals: list[BioSignal] = [],
) -> Planet:
    return Planet(
        system_name=StarSystem or "DONT CARE",
        SystemAddress=SystemAddress or PRIMARY_SYSTEM_ADDRESS,
        BodyName=BodyName or "DOESNT MATTER",
        BodyID=BodyID or PRIMARY_PLANET_ID,
        planet_class=planet_class or ROCKY,
        terraformable=terraformable,
        detailed_scan_by_player=detailed_scan_by_player,
        was_discovered=was_discovered,
        was_mapped=was_mapped,
        mapped_by_player=mapped_by_player,
        atmosphere=atmosphere or "None",
        surface_gravity=(gravity or 0) * 10,
        mass_em=mass,
        signal_count=signal_count or 0,
        signals=signals,
    )
