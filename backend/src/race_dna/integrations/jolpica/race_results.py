from datetime import date
from decimal import Decimal

from pydantic import BaseModel, Field

from race_dna.integrations.jolpica.schemas import JolpicaDriver


class JolpicaLocation(BaseModel):
    locality: str
    country: str


class JolpicaCircuit(BaseModel):
    circuit_id: str = Field(alias="circuitId")
    circuit_name: str = Field(alias="circuitName")
    location: JolpicaLocation = Field(alias="Location")


class JolpicaConstructor(BaseModel):
    constructor_id: str = Field(alias="constructorId")
    name: str
    nationality: str


class JolpicaRaceResult(BaseModel):
    number: int
    position: int
    position_text: str = Field(alias="positionText")
    points: Decimal
    driver: JolpicaDriver = Field(alias="Driver")
    constructor: JolpicaConstructor = Field(alias="Constructor")
    grid: int
    laps: int
    status: str


class JolpicaRace(BaseModel):
    season: int
    round: int
    race_name: str = Field(alias="raceName")
    circuit: JolpicaCircuit = Field(alias="Circuit")
    date: date
    results: list[JolpicaRaceResult] = Field(alias="Results")


class JolpicaRaceTable(BaseModel):
    races: list[JolpicaRace] = Field(alias="Races")


class JolpicaRaceResultsMRData(BaseModel):
    limit: int
    offset: int
    total: int
    race_table: JolpicaRaceTable = Field(alias="RaceTable")


class JolpicaRaceResultsResponse(BaseModel):
    mr_data: JolpicaRaceResultsMRData = Field(alias="MRData")