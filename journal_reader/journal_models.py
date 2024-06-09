import json
from typing import Literal, Optional
from pydantic import BaseModel

from values import HMCB


EventType = (
    Literal["FSDTarget"]
    | Literal["LeaveBody"]
    | Literal["Liftoff"]
    | Literal["Scan"]
    | Literal["ScanOrganic"]
    | Literal["SellExplorationData"]
    | Literal["SellOrganicData"]
    | Literal["Touchdown"]
)


class JournalEvent(BaseModel):
    timestamp: str
    event: EventType


class SellCartographicsEvent(JournalEvent):
    Systems: list[str]
    Discovered: list[str]
    BaseValue: int
    Bonus: int
    TotalEarnings: int


class BioData(BaseModel):
    Genus_Localised: str
    Species_Localised: str
    Variant_Localised: str
    Value: int
    Bonus: int


class SellOrganicDataEvent(JournalEvent):
    BioData: list[BioData]


class SystemEvent(JournalEvent):
    StarSystem: str


class BodyEvent(SystemEvent):
    BodyName: str


class ScanEvent(BodyEvent):
    ScanType: Literal["AutoScan"] | Literal["Detailed"] | Literal["Basic"]
    PlanetClass: str | None = None
    TerraformState: str | None = None
    DistanceFromArrivalLS: Optional[float] = None
    AtmosphereType: Optional[str] = None
    SurfaceGravity: Optional[float] = None
    SurfaceTemperature: Optional[float] = None
    Landable: Optional[bool] = None
    SemiMajorAxis: Optional[float] = None
    WasDiscovered: bool
    WasMapped: bool


class ScanOrganicEvent(JournalEvent):
    ScanType: Literal["Log"] | Literal["Sample"] | Literal["Analyse"]
    Genus_Localised: str
    Species_Localised: str
    Variant_Localised: str
    SystemAddress: int
    Body: int


event_mapping = {
    "Scan": ScanEvent,
    "ScanOrganic": ScanOrganicEvent,
    "SellExplorationData": SellCartographicsEvent,
    "SellOrganicData": SellOrganicDataEvent,
}


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

    def get_until_event(
        self, event_types: list[EventType], reverse: bool = False
    ) -> list[JournalEvent]:
        """Get all events (from start by default) until event of target type is found."""
        matching_events: list[JournalEvent] = []
        dataset = [*self.events]
        if reverse:
            dataset = list(reversed(dataset))

        for event in dataset:
            if event.event in event_types:
                break
            matching_events.append(event)

        if reverse:
            matching_events = list(reversed(matching_events))
        return matching_events
