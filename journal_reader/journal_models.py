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

    def convert_str_to_event(self, data: str | JournalEvent) -> JournalEvent | None:
        if isinstance(data, JournalEvent):
            return data
        parsed = json.loads(data)
        event_type = event_mapping.get(parsed["event"], None)
        if event_type is not None:
            return event_type(**parsed)

    def append(self, data: str | JournalEvent) -> None:
        event = self.convert_str_to_event(data)
        if event is not None:
            self.events.append(event)

    def find_event(
        self, data: str | JournalEvent, reverse: bool = False
    ) -> JournalEvent | None:
        """
        Pass in either a raw journal str or processed event, receive the first matching event
        (from oldest to newest by default).
        """
        event = self.convert_str_to_event(data) if isinstance(data, str) else data
        if event is None:
            return

        dataset = [*self.events]
        if reverse:
            dataset = list(reversed(dataset))
        for logged_event in dataset:
            if (
                event.timestamp == logged_event.timestamp
                and event.event == logged_event.event
            ):
                return logged_event
