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
                    "dna/overtake"
                ),
                params={"season": 2023},
            )
    finally:
        app.dependency_overrides.pop(get_db_session, None)


def test_overtake_endpoint_exposes_proxy_calculation() -> None:
    response = request_metric(
        [
            SimpleNamespace(
                grid_position=5,
                finish_position=1,
                status="Finished",
            )
        ]
    )

    assert response.status_code == 200
    assert response.json() == {
        "season": 2023,
        "metric": "overtake_index",
        "methodology_version": "1.0",
        "proxy": True,
        "score": 100.0,
        "sample_size": 1,
        "eligible_races": 1,
        "total_positions_gained": 4,
        "total_available_positions": 4,
        "components": [
            {
                "key": "opportunity_conversion",
                "weight": 0.6,
                "raw_value": 100.0,
                "score": 100.0,
            },
            {
                "key": "gain_frequency",
                "weight": 0.4,
                "raw_value": 100.0,
                "score": 100.0,
            },
        ],
    }


def test_overtake_endpoint_rejects_ineligible_data() -> None:
    response = request_metric(
        [
            SimpleNamespace(
                grid_position=1,
                finish_position=1,
                status="Finished",
            )
        ]
    )

    assert response.status_code == 422
    assert response.json() == {
        "detail": (
            "At least one eligible race sample is required."
        )
    }