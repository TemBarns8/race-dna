from pydantic import BaseModel, Field


class SeasonStats(BaseModel):
    season: int = Field(ge=1950)
    races: int = Field(ge=0)
    wins: int = Field(ge=0)
    podiums: int = Field(ge=0)
    qualifying_sessions: int = Field(ge=0)
    poles: int = Field(ge=0)
    p1_starts: int = Field(ge=0)
    race_points: float = Field(ge=0)