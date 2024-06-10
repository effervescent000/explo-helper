from typing import Literal
from conftest import PRIMARY_PLANET_ID, PRIMARY_SYSTEM_ADDRESS
from journal_reader.journal_models import EventType, JournalEvent, ScanEvent
from values import ROCKY


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
        WasDiscovered=WasDiscovered or False,
        WasMapped=WasMapped or False,
    )
