from collections.abc import AsyncIterator
from decimal import Decimal
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
                    SimpleNamespace(
                        _mapping={
                            "season": 2019,
                            "races": 21,
                            "wins": 3,
                            "podiums": 9,
                            "p1_starts": 2,
                            "race_points": Decimal("278.00"),
                        }
                    )
                ],
            ),
            FakeResult(
                rows=[
                    SimpleNamespace(
                        _mapping={
                            "season": 2019,
                            "qualifying_sessions": 21,
                            "poles": 3,
                        }
                    ),
                    SimpleNamespace(
                        _mapping={
                            "season": 2026,
                            "qualifying_sessions": 1,
                            "poles": 0,
                        }
                    ),
                ],
            ),
        ]

    async def execute(self, statement: Any) -> FakeResult:
        return self.results.pop(0)


def test_driver_seasons_combines_race_and_qualifying_stats() -> None:
    fake_session = FakeSession()

    async def override_get_db_session() -> AsyncIterator[FakeSession]:
        yield fake_session

    app.dependency_overrides[
        get_db_session
    ] = override_get_db_session

    try:
        with TestClient(app) as client:
            response = client.get(
                "/api/v1/drivers/max-verstappen/seasons"
            )
    finally:
        app.dependency_overrides.pop(get_db_session, None)

    assert response.status_code == 200
    assert response.json() == [
        {
            "season": 2019,
            "races": 21,
            "wins": 3,
            "podiums": 9,
            "qualifying_sessions": 21,
            "poles": 3,
            "p1_starts": 2,
            "race_points": 278.0,
        },
        {
            "season": 2026,
            "races": 0,
            "wins": 0,
            "podiums": 0,
            "qualifying_sessions": 1,
            "poles": 0,
            "p1_starts": 0,
            "race_points": 0.0,
        },
    ]