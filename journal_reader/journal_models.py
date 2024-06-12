from typing import Any, Literal, Optional
from pydantic import BaseModel


EventType = (
    Literal["DiscoveryScan"]
    | Literal["FSDJump"]
    | Literal["FSSBodySignals"]
    | Literal["LeaveBody"]
    | Literal["Liftoff"]
    | Literal["SAAScanComplete"]
    | Literal["SAASignalsFound"]
    | Literal["Scan"]
    | Literal["ScanOrganic"]
    | Literal["SellExplorationData"]
    | Literal["SellOrganicData"]
    | Literal["Touchdown"]
)


class JournalEvent(BaseModel):
    timestamp: str
    event: EventType

    def dump(self) -> dict[str, Any]:
        """Meant to be overridden by subclasses."""
        return {}


class FSDJumpEvent(JournalEvent):
    StarSystem: str
    SystemAddress: int
    StarPos: list[float]

    def dump(self) -> dict[str, Any]:
        return {
            "system_name": self.StarSystem,
            "system_address": self.SystemAddress,
            "star_pos": self.StarPos,
        }


class GenericSignal(BaseModel):
    Type: str
    Type_Localised: str | None = None
    Count: int


class FSSSignalEvent(JournalEvent):
    BodyID: int
    SystemAddress: int
    Signals: list[GenericSignal] = []


class Genus(BaseModel):
    Genus: str
    Genus_Localised: str


class DSSSignalEvent(JournalEvent):
    BodyID: int
    SystemAddress: int
    Signals: list[GenericSignal] = []
    Genuses: list[Genus] = []


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


class ScanEvent(JournalEvent):
    ScanType: Literal["AutoScan"] | Literal["Detailed"] | Literal["Basic"]
    StarSystem: str
    SystemAddress: int
    BodyName: str
    BodyID: int
    PlanetClass: str | None = None
    TerraformState: str | None = None
    DistanceFromArrivalLS: Optional[float] = None
    AtmosphereType: Optional[str] = None
    SurfaceGravity: Optional[float] = None
    SurfaceTemperature: Optional[float] = None
    Landable: Optional[bool] = None
    SemiMajorAxis: Optional[float] = None
    MassEM: float | None = None
    WasDiscovered: bool
    WasMapped: bool


class DiscoveryScanEvent(JournalEvent):
    SystemAddress: int
    Bodies: int


class ScanOrganicEvent(JournalEvent):
    ScanType: Literal["Log"] | Literal["Sample"] | Literal["Analyse"]
    Genus_Localised: str
    Species_Localised: str
    Variant_Localised: str
    SystemAddress: int
    Body: int


class DSSEvent(JournalEvent):
    SystemAddress: int
    BodyName: str
    BodyID: int
    ProbesUsed: int
    EfficiencyTarget: int


event_mapping = {
    "DiscoveryScan": DiscoveryScanEvent,
    "FSDJump": FSDJumpEvent,
    "FSSBodySignals": FSSSignalEvent,
    "SAAScanComplete": DSSEvent,
    "SAASignalsFound": DSSSignalEvent,
    "Scan": ScanEvent,
    "ScanOrganic": ScanOrganicEvent,
    "SellExplorationData": SellCartographicsEvent,
    "SellOrganicData": SellOrganicDataEvent,
}
