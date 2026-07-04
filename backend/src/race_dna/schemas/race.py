from datetime import date

from pydantic import BaseModel, ConfigDict


class DriverRaceResultRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    season: int
    round: int
    race_name: str
    race_date: date

    circuit_id: str
    circuit_name: str
    locality: str
    country: str

    constructor_id: str
    constructor_name: str
    car_number: int

    grid_position: int
    finish_position: int
    position_text: str
    points: float
    laps: int
    status: str