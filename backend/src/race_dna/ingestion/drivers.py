from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from race_dna.db.models import Driver
from race_dna.integrations.jolpica.client import JolpicaClient
from race_dna.integrations.jolpica.mapping import (
    map_jolpica_driver,
)


async def sync_driver(
    session: AsyncSession,
    client: JolpicaClient,
    driver_id: str,
) -> tuple[Driver, bool]:
    source_driver = await client.get_driver(driver_id)
    payload = map_jolpica_driver(source_driver)

    result = await session.execute(
        select(Driver).where(Driver.slug == payload.slug)
    )
    driver = result.scalar_one_or_none()
    created = driver is None

    if driver is None:
        driver = Driver(**payload.model_dump())
        session.add(driver)
    else:
        for field, value in payload.model_dump().items():
            setattr(driver, field, value)

    await session.commit()
    await session.refresh(driver)

    return driver, created