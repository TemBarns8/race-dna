from collections.abc import AsyncIterator
from datetime import date
from decimal import Decimal
from types import SimpleNamespace
from typing import Any
from uuid import uuid4

from fastapi.testclient import TestClient

from race_dna.database import get_db_session
from race_dna.main import app
from race_dna.schemas.race import DriverRaceResultRead


RACE_DATA = {
    "season": 2023,
    "round": 1,
    "race_name": "Bahrain Grand Prix",
    "race_date": date(2023, 3, 5),
    "circuit_id": "bahrain",
    "circuit_name": "Bahrain International Circuit",
    "locality": "Sakhir",
    "country": "Bahrain",
    "constructor_id": "red_bull",
    "constructor_name": "Red Bull",
    "car_number": 1,
    "grid_position": 1,
    "finish_position": 1,
    "position_text": "1",
    "points": Decimal("25.00"),
    "laps": 57,
    "status": "Finished",
}


class FakeResult:
    def __init__(
        self,
        *,
        scalar: object | None = None,
        rows: list[object] | None = None,
    ) -> None:
        self.scalar = scalar
        self.rows = rows or []

    def scalar_one_or_none(self) -> object | None:
        return self.scalar

    def __iter__(self):
        return iter(self.rows)


class FakeSession:
    def __init__(self) -> None:
        self.results = [
            FakeResult(
                scalar=SimpleNamespace(id=uuid4()),
            ),
            FakeResult(
                rows=[
                    SimpleNamespace(_mapping=RACE_DATA),
                ],
            ),
        ]

    async def execute(self, statement: Any) -> FakeResult:
        return self.results.pop(0)


def test_race_schema_converts_database_values() -> None:
    race = DriverRaceResultRead.model_validate(RACE_DATA)

    assert race.race_date == date(2023, 3, 5)
    assert race.points == 25.0
    assert race.finish_position == 1


def test_driver_races_endpoint_returns_filtered_results() -> None:
    fake_session = FakeSession()

    async def override_get_db_session() -> AsyncIterator[FakeSession]:
        yield fake_session

    app.dependency_overrides[
        get_db_session
    ] = override_get_db_session

    try:
        with TestClient(app) as client:
            response = client.get(
                "/api/v1/drivers/max-verstappen/races",
                params={"season": 2023},
            )
    finally:
        app.dependency_overrides.pop(get_db_session, None)

    assert response.status_code == 200
    assert response.json() == [
        {
            **RACE_DATA,
            "race_date": "2023-03-05",
            "points": 25.0,
        }
    ]