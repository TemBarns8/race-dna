from dataclasses import dataclass
from uuid import uuid4

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from race_dna.db.models import (
    Driver,
    DriverQualifyingResult,
    Race,
    Season,
)
from race_dna.ingestion.race_results import (
    DriverNotSynchronizedError,
)
from race_dna.integrations.jolpica.client import JolpicaClient


@dataclass(frozen=True)
class QualifyingResultsSyncSummary:
    received: int
    seasons_created: int
    races_created: int
    qualifying_created: int
    qualifying_updated: int


async def sync_driver_qualifying_results(
    session: AsyncSession,
    client: JolpicaClient,
    driver_id: str,
) -> QualifyingResultsSyncSummary:
    slug = driver_id.replace("_", "-")

    driver_result = await session.execute(
        select(Driver).where(Driver.slug == slug)
    )
    driver = driver_result.scalar_one_or_none()

    if driver is None:
        raise DriverNotSynchronizedError(
            f"Synchronize driver '{driver_id}' first."
        )

    source_races = (
        await client.get_driver_qualifying_results(driver_id)
    )

    seasons = {
        season.year: season
        for season in (
            await session.execute(select(Season))
        ).scalars()
    }
    races = {
        (race.season_year, race.round): race
        for race in (
            await session.execute(select(Race))
        ).scalars()
    }
    existing_results = {
        result.race_id: result
        for result in (
            await session.execute(
                select(DriverQualifyingResult).where(
                    DriverQualifyingResult.driver_id == driver.id
                )
            )
        ).scalars()
    }

    seasons_created = 0
    races_created = 0
    qualifying_created = 0
    qualifying_updated = 0

    # Phase 1: create seasons.
    for source_race in source_races:
        if source_race.season not in seasons:
            season = Season(year=source_race.season)
            session.add(season)
            seasons[source_race.season] = season
            seasons_created += 1

    await session.flush()

    # Phase 2: create or update races.
    for source_race in source_races:
        race_key = (source_race.season, source_race.round)
        race = races.get(race_key)

        race_values = {
            "name": source_race.race_name,
            "date": source_race.date,
            "circuit_id": source_race.circuit.circuit_id,
            "circuit_name": source_race.circuit.circuit_name,
            "locality": source_race.circuit.location.locality,
            "country": source_race.circuit.location.country,
        }

        if race is None:
            race = Race(
                id=uuid4(),
                season_year=source_race.season,
                round=source_race.round,
                **race_values,
            )
            session.add(race)
            races[race_key] = race
            races_created += 1
        else:
            for field, value in race_values.items():
                setattr(race, field, value)

    await session.flush()

    # Phase 3: create or update qualifying results.
    for source_race in source_races:
        if not source_race.qualifying_results:
            continue

        race_key = (source_race.season, source_race.round)
        race = races[race_key]
        source_result = source_race.qualifying_results[0]
        result = existing_results.get(race.id)

        result_values = {
            "car_number": source_result.number,
            "position": source_result.position,
            "constructor_id": (
                source_result.constructor.constructor_id
            ),
            "constructor_name": source_result.constructor.name,
            "q1": source_result.q1,
            "q2": source_result.q2,
            "q3": source_result.q3,
        }

        if result is None:
            result = DriverQualifyingResult(
                driver_id=driver.id,
                race_id=race.id,
                **result_values,
            )
            session.add(result)
            existing_results[race.id] = result
            qualifying_created += 1
        else:
            for field, value in result_values.items():
                setattr(result, field, value)
            qualifying_updated += 1

    await session.commit()

    return QualifyingResultsSyncSummary(
        received=len(source_races),
        seasons_created=seasons_created,
        races_created=races_created,
        qualifying_created=qualifying_created,
        qualifying_updated=qualifying_updated,
    )