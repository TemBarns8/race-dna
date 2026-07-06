from pydantic import BaseModel, ConfigDict, Field


class MetricComponentRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    key: str
    weight: float = Field(ge=0, le=1)
    raw_value: float | None
    score: float = Field(ge=0, le=100)


class ConsistencyIndexRead(BaseModel):
    season: int = Field(ge=1950)
    metric: str
    methodology_version: str
    score: float = Field(ge=0, le=100)
    sample_size: int = Field(ge=1)
    completed_races: int = Field(ge=0)
    median_finish: float | None
    components: list[MetricComponentRead]


class OvertakeIndexRead(BaseModel):
    season: int = Field(ge=1950)
    metric: str
    methodology_version: str
    proxy: bool
    score: float = Field(ge=0, le=100)
    sample_size: int = Field(ge=1)
    eligible_races: int = Field(ge=1)
    total_positions_gained: int = Field(ge=0)
    total_available_positions: int = Field(ge=1)
    components: list[MetricComponentRead]