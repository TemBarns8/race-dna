from collections.abc import AsyncIterator
from types import SimpleNamespace
from typing import Any
from uuid import uuid4

from fastapi.testclient import TestClient

from race_dna.database import get_db_session
from race_dna.main import app


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

    def all(self) -> list[object]:
        return self.rows


class FakeSession:
    def __init__(self, rows: list[object]) -> None:
        self.results = [
            FakeResult(
                scalar=SimpleNamespace(id=uuid4()),
            ),
            FakeResult(rows=rows),
        ]

    async def execute(self, statement: Any) -> FakeResult:
        return self.results.pop(0)


def request_metric(rows: list[object]):
    fake_session = FakeSession(rows)

    async def override_get_db_session() -> AsyncIterator[FakeSession]:
        yield fake_session

    app.dependency_overrides[
        get_db_session
    ] = override_get_db_session

    try:
        with TestClient(app) as client:
            return client.get(
                (
                    "/api/v1/drivers/max-verstappen/"
                    "dna/consistency"
                ),
                params={"season": 2023},
            )
    finally:
        app.dependency_overrides.pop(get_db_session, None)


def test_consistency_endpoint_exposes_calculation() -> None:
    response = request_metric(
        [
            SimpleNamespace(
                finish_position=1,
                status="Finished",
            ),
            SimpleNamespace(
                finish_position=1,
                status="+1 Lap",
            ),
        ]
    )

    assert response.status_code == 200
    assert response.json() == {
        "season": 2023,
        "metric": "consistency_index",
        "methodology_version": "1.0",
        "score": 100.0,
        "sample_size": 2,
        "completed_races": 2,
        "median_finish": 1.0,
        "components": [
            {
                "key": "finish_stability",
                "weight": 0.7,
                "raw_value": 0.0,
                "score": 100.0,
            },
            {
                "key": "completion_rate",
                "weight": 0.3,
                "raw_value": 100.0,
                "score": 100.0,
            },
        ],
    }


def test_consistency_endpoint_rejects_missing_season_data() -> None:
    response = request_metric([])

    assert response.status_code == 404
    assert response.json() == {
        "detail": (
            "No race results for driver 'max-verstappen' "
            "in season 2023."
        )
    }