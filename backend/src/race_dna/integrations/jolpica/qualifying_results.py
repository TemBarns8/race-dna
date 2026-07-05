from datetime import date

from pydantic import BaseModel, Field

from race_dna.integrations.jolpica.race_results import (
    JolpicaCircuit,
    JolpicaConstructor,
)
from race_dna.integrations.jolpica.schemas import JolpicaDriver


class JolpicaQualifyingResult(BaseModel):
    number: int
    position: int
    driver: JolpicaDriver = Field(alias="Driver")
    constructor: JolpicaConstructor = Field(alias="Constructor")
    q1: str | None = Field(default=None, alias="Q1")
    q2: str | None = Field(default=None, alias="Q2")
    q3: str | None = Field(default=None, alias="Q3")


class JolpicaQualifyingRace(BaseModel):
    season: int
    round: int
    race_name: str = Field(alias="raceName")
    circuit: JolpicaCircuit = Field(alias="Circuit")
    date: date
    qualifying_results: list[JolpicaQualifyingResult] = Field(
        alias="QualifyingResults"
    )


class JolpicaQualifyingRaceTable(BaseModel):
    races: list[JolpicaQualifyingRace] = Field(alias="Races")


class JolpicaQualifyingMRData(BaseModel):
    limit: int
    offset: int
    total: int
    race_table: JolpicaQualifyingRaceTable = Field(
        alias="RaceTable"
    )


class JolpicaQualifyingResponse(BaseModel):
    mr_data: JolpicaQualifyingMRData = Field(alias="MRData")