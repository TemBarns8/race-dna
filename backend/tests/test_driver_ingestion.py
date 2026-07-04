import asyncio
from unittest.mock import AsyncMock, MagicMock

from sqlalchemy.ext.asyncio import AsyncSession

from race_dna.db.models import Driver
from race_dna.ingestion.drivers import sync_driver
from race_dna.integrations.jolpica.client import JolpicaClient
from race_dna.integrations.jolpica.schemas import JolpicaDriver


def make_source_driver() -> JolpicaDriver:
    return JolpicaDriver.model_validate(
        {
            "driverId": "max_verstappen",
            "permanentNumber": "3",
            "code": "VER",
            "url": (
                "http://en.wikipedia.org/wiki/"
                "Max_Verstappen"
            ),
            "givenName": "Max",
            "familyName": "Verstappen",
            "dateOfBirth": "1997-09-30",
            "nationality": "Dutch",
        }
    )


def test_sync_driver_updates_existing_driver() -> None:
    existing = Driver(
        slug="max-verstappen",
        given_name="Max",
        family_name="Verstappen",
        code="VER",
        permanent_number=33,
        country_code="NL",
        date_of_birth=make_source_driver().date_of_birth,
    )

    result = MagicMock()
    result.scalar_one_or_none.return_value = existing

    session = AsyncMock(spec=AsyncSession)
    session.execute.return_value = result

    client = AsyncMock(spec=JolpicaClient)
    client.get_driver.return_value = make_source_driver()

    driver, created = asyncio.run(
        sync_driver(
            session=session,
            client=client,
            driver_id="max_verstappen",
        )
    )

    assert created is False
    assert driver.permanent_number == 3
    session.commit.assert_awaited_once()
    session.refresh.assert_awaited_once_with(existing)


def test_sync_driver_creates_missing_driver() -> None:
    result = MagicMock()
    result.scalar_one_or_none.return_value = None

    session = AsyncMock(spec=AsyncSession)
    session.execute.return_value = result

    client = AsyncMock(spec=JolpicaClient)
    client.get_driver.return_value = make_source_driver()

    driver, created = asyncio.run(
        sync_driver(
            session=session,
            client=client,
            driver_id="max_verstappen",
        )
    )

    assert created is True
    assert driver.slug == "max-verstappen"
    session.add.assert_called_once_with(driver)
    session.commit.assert_awaited_once()