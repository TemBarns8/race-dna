from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from race_dna.database import get_db_session
from race_dna.db.models import Driver, DriverRaceResult, Race
from race_dna.metrics.consistency import (
    RaceConsistencySample,
    calculate_consistency_index,
)

from race_dna.metrics.overtake import (
    RaceOvertakeSample,
    calculate_overtake_index,
)
from race_dna.schemas.metric import (
    ConsistencyIndexRead,
    MetricComponentRead,
    OvertakeIndexRead,
)


router = APIRouter(
    prefix="/drivers/{slug}/dna",
    tags=["dna"],
)

DatabaseSession = Annotated[
    AsyncSession,
    Depends(get_db_session),
]


@router.get(
    "/consistency",
    response_model=ConsistencyIndexRead,
)
async def get_consistency_index(
    slug: str,
    session: DatabaseSession,
    season: int = Query(ge=1950),
) -> ConsistencyIndexRead:
    driver_result = await session.execute(
        select(Driver).where(Driver.slug == slug)
    )
    driver = driver_result.scalar_one_or_none()

    if driver is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Driver '{slug}' was not found.",
        )

    race_results = await session.execute(
        select(
            DriverRaceResult.finish_position,
            DriverRaceResult.status,
        )
        .select_from(DriverRaceResult)
        .join(
            Race,
            Race.id == DriverRaceResult.race_id,
        )
        .where(
            DriverRaceResult.driver_id == driver.id,
            Race.season_year == season,
        )
        .order_by(Race.round)
    )
    rows = race_results.all()

    if not rows:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=(
                f"No race results for driver '{slug}' "
                f"in season {season}."
            ),
        )

    samples = [
        RaceConsistencySample(
            finish_position=row.finish_position,
            status=row.status,
        )
        for row in rows
    ]
    result = calculate_consistency_index(samples)

    return ConsistencyIndexRead(
        season=season,
        metric=result.metric,
        methodology_version=result.methodology_version,
        score=result.score,
        sample_size=result.sample_size,
        completed_races=result.completed_races,
        median_finish=result.median_finish,
        components=[
            MetricComponentRead.model_validate(component)
            for component in result.components
        ],
    )

@router.get(
    "/overtake",
    response_model=OvertakeIndexRead,
)
async def get_overtake_index(
    slug: str,
    session: DatabaseSession,
    season: int = Query(ge=1950),
) -> OvertakeIndexRead:
    driver_result = await session.execute(
        select(Driver).where(Driver.slug == slug)
    )
    driver = driver_result.scalar_one_or_none()

    if driver is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Driver '{slug}' was not found.",
        )

    race_results = await session.execute(
        select(
            DriverRaceResult.grid_position,
            DriverRaceResult.finish_position,
            DriverRaceResult.status,
        )
        .select_from(DriverRaceResult)
        .join(
            Race,
            Race.id == DriverRaceResult.race_id,
        )
        .where(
            DriverRaceResult.driver_id == driver.id,
            Race.season_year == season,
        )
        .order_by(Race.round)
    )
    rows = race_results.all()

    if not rows:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=(
                f"No race results for driver '{slug}' "
                f"in season {season}."
            ),
        )

    samples = [
        RaceOvertakeSample(
            grid_position=row.grid_position,
            finish_position=row.finish_position,
            status=row.status,
        )
        for row in rows
    ]

    try:
        result = calculate_overtake_index(samples)
    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=str(error),
        ) from error

    return OvertakeIndexRead(
        season=season,
        metric=result.metric,
        methodology_version=result.methodology_version,
        proxy=result.proxy,
        score=result.score,
        sample_size=result.sample_size,
        eligible_races=result.eligible_races,
        total_positions_gained=(
            result.total_positions_gained
        ),
        total_available_positions=(
            result.total_available_positions
        ),
        components=[
            MetricComponentRead.model_validate(component)
            for component in result.components
        ],
    )