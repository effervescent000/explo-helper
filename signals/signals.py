from typing import Literal
from pydantic import BaseModel

STANDARD_MAX_GRAVITY = 0.27

AtmosphereTypes = (
    Literal["None"]
    | Literal["Argon"]
    | Literal["Neon"]
    | Literal["Ammonia"]
    | Literal["CarbonDioxide"]
    | Literal["CarbonDioxideRich"]
    | Literal["Nitrogen"]
    | Literal["Water"]
    | Literal["WaterRich"]
)


class Flora(BaseModel):
    genus: str
    species: str | None = None
    min_distance_between: int
    atmosphere_requirement: list[AtmosphereTypes] | None = None
    max_gravity: float | None = None
    min_temperature_k: int | None = None
    max_temperature_k: int | None = None


concha_defaults = Flora(
    genus="Concha", min_distance_between=150, max_gravity=STANDARD_MAX_GRAVITY
).model_dump(exclude_none=True)

species = [
    Flora(
        **concha_defaults,
        species="aureolas",
        atmosphere_requirement=["Ammonia"],
    ),
    Flora(**concha_defaults, atmosphere_requirement=["Nitrogen"], species="biconcavis"),
    Flora(
        **concha_defaults,
        atmosphere_requirement=["CarbonDioxide", "CarbonDioxideRich"],
        max_temperature_k=190,
        species="labiata",
    ),
]
