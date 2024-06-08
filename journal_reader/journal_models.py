import json
from typing import Literal, Optional
from pydantic import BaseModel


EventType = (
    Literal["FSDTarget"]
    | Literal["LeaveBody"]
    | Literal["Liftoff"]
    | Literal["Scan"]
    | Literal["Touchdown"]
)


class JournalEvent(BaseModel):
    timestamp: str
    event: EventType


class SystemEvent(JournalEvent):
    StarSystem: str


class BodyEvent(SystemEvent):
    BodyName: str


class ScanEvent(BodyEvent):
    ScanType: Literal["AutoScan"] | Literal["Detailed"] | Literal["Basic"]
    DistanceFromArrivalLS: Optional[float] = None
    AtmosphereType: Optional[str] = None
    SurfaceGravity: Optional[float] = None
    SurfaceTemperature: Optional[float] = None
    Landable: Optional[bool] = None
    SemiMajorAxis: Optional[float] = None
    WasDiscovered: bool
    WasMapped: bool


event_mapping = {"Scan": ScanEvent}


class Log(BaseModel):
    events: list[JournalEvent] = []

    def append(self, data: str) -> None:
        parsed = json.loads(data)
        event_type = event_mapping.get(parsed["event"], None)
        if event_type is not None:
            self.events.append(event_type(**parsed))
