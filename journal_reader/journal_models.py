from enum import Enum
from typing import Literal
from pydantic import BaseModel

EventType = Enum("EventType", ["FSDTarget", "LeaveBody", "Liftoff", "Touchdown"])


class JournalEvent(BaseModel):
    timestamp: str
    event: EventType


class SystemEvent(JournalEvent):
    StarSystem: str


class BodyEvent(SystemEvent):
    BodyName: str


class ScanEvent(BodyEvent):
    ScanType: Literal["Autoscan"] | Literal["Detailed"] | Literal["Basic"]
    DistanceFromArrivalLS: float
    AtmosphereType: str
    SurfaceGravity: float
    SurfaceTemperature: float
    Landable: bool
    SemiMajorAxis: float
    WasDiscovered: bool
    WasMapped: bool


event_mapping = {"Scan": ScanEvent}


class Log(BaseModel):
    events: list[JournalEvent] = []

    def append(self, data: JournalEvent) -> None:
        event_type = event_mapping.get(data.event.name, None)
        if event_type is not None:
            self.events.append(event_type(**data.model_dump()))
