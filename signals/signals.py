from typing import Literal, Tuple, get_args
from pydantic import BaseModel

STANDARD_MAX_GRAVITY = 0.27

AtmosphereTypes = Literal[
    "None",
    "Ammonia",
    "Argon",
    "CarbonDioxide",
    "CarbonDioxideRich",
    "Helium",
    "Neon",
    "Nitrogen",
    "Water",
    "WaterRich",
]

atmospheres: Tuple[AtmosphereTypes, ...] = get_args(AtmosphereTypes)


class Flora(BaseModel):
    genus: str
    species: str | None = None
    value: int | None = None
    min_distance_between: int
    atmosphere_requirement: list[AtmosphereTypes] | None = None
    max_gravity: float | None = None
    min_temperature_k: int | None = None
    max_temperature_k: int | None = None


bacteria_defaults = Flora(genus="Bacterium", min_distance_between=500).model_dump(
    exclude_none=True
)
concha_defaults = Flora(
    genus="Concha", min_distance_between=150, max_gravity=STANDARD_MAX_GRAVITY
).model_dump(exclude_none=True)

species = [
    # BACTERIA
    Flora(
        **bacteria_defaults,
        species="nebulus",
        atmosphere_requirement=["Helium"],
        value=5_289_900,
    ),
    Flora(
        **bacteria_defaults,
        species="tela",
        atmosphere_requirement=[x for x in atmospheres if x != "None"],
        value=1_000_000,
    ),
    # CONCHA
    Flora(
        **concha_defaults,
        species="aureolas",
        atmosphere_requirement=["Ammonia"],
        value=7_774_700,
    ),
    Flora(
        **concha_defaults,
        atmosphere_requirement=["Nitrogen"],
        species="biconcavis",
        value=19_010_800,
    ),
    Flora(
        **concha_defaults,
        atmosphere_requirement=["CarbonDioxide", "CarbonDioxideRich"],
        max_temperature_k=190,
        species="labiata",
        value=2_352_400,
    ),
]
