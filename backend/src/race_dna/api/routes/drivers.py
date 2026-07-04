from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from race_dna.database import get_db_session
from race_dna.db.models import Driver, DriverRaceResult, Race
from race_dna.schemas.driver import DriverCreate, DriverRead
from race_dna.schemas.season import SeasonStats
from race_dna.schemas.race import DriverRaceResultRead

router = APIRouter(
    prefix="/drivers",
    tags=["drivers"],
)

DatabaseSession = Annotated[
    AsyncSession,
    Depends(get_db_session),
]


@router.post(
    "",
    response_model=DriverRead,
    status_code=status.HTTP_201_CREATED,
)
async def create_driver(
    payload: DriverCreate,
    session: DatabaseSession,
) -> Driver:
    driver = Driver(**payload.model_dump())
    session.add(driver)

    try:
        await session.commit()
    except IntegrityError as error:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Driver '{payload.slug}' already exists.",
        ) from error

    await session.refresh(driver)
    return driver


@router.get(
    "/{slug}",
    response_model=DriverRead,
)
async def get_driver(
    slug: str,
    session: DatabaseSession,
) -> Driver:
    result = await session.execute(
        select(Driver).where(Driver.slug == slug)
    )
    driver = result.scalar_one_or_none()

    if driver is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Driver '{slug}' was not found.",
        )

    return driver

@router.get(
    "/{slug}/seasons",
    response_model=list[SeasonStats],
)
async def get_driver_seasons(
    slug: str,
    session: DatabaseSession,
) -> list[SeasonStats]:
    driver_result = await session.execute(
        select(Driver).where(Driver.slug == slug)
    )
    driver = driver_result.scalar_one_or_none()

    if driver is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Driver '{slug}' was not found.",
        )

    stats_result = await session.execute(
        select(
            Race.season_year.label("season"),
            func.count(DriverRaceResult.id).label("races"),
            func.count(DriverRaceResult.id)
            .filter(DriverRaceResult.finish_position == 1)
            .label("wins"),
            func.count(DriverRaceResult.id)
            .filter(DriverRaceResult.finish_position <= 3)
            .label("podiums"),
            func.count(DriverRaceResult.id)
            .filter(DriverRaceResult.grid_position == 1)
            .label("p1_starts"),
            func.sum(DriverRaceResult.points).label(
                "race_points"
            ),
        )
        .join(
            Race,
            Race.id == DriverRaceResult.race_id,
        )
        .where(DriverRaceResult.driver_id == driver.id)
        .group_by(Race.season_year)
        .order_by(Race.season_year)
    )

    return [
        SeasonStats.model_validate(row._mapping)
        for row in stats_result
    ]

@router.get(
    "/{slug}/races",
    response_model=list[DriverRaceResultRead],
)
async def get_driver_races(
    slug: str,
    session: DatabaseSession,
    season: int | None = Query(default=None, ge=1950),
) -> list[DriverRaceResultRead]:
    driver_result = await session.execute(
        select(Driver).where(Driver.slug == slug)
    )
    driver = driver_result.scalar_one_or_none()

    if driver is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Driver '{slug}' was not found.",
        )

    statement = (
        select(
            Race.season_year.label("season"),
            Race.round,
            Race.name.label("race_name"),
            Race.date.label("race_date"),
            Race.circuit_id,
            Race.circuit_name,
            Race.locality,
            Race.country,
            DriverRaceResult.constructor_id,
            DriverRaceResult.constructor_name,
            DriverRaceResult.car_number,
            DriverRaceResult.grid_position,
            DriverRaceResult.finish_position,
            DriverRaceResult.position_text,
            DriverRaceResult.points,
            DriverRaceResult.laps,
            DriverRaceResult.status,
        )
        .select_from(DriverRaceResult)
        .join(
            Race,
            Race.id == DriverRaceResult.race_id,
        )
        .where(DriverRaceResult.driver_id == driver.id)
        .order_by(Race.season_year, Race.round)
    )

    if season is not None:
        statement = statement.where(
            Race.season_year == season
        )

    races_result = await session.execute(statement)

    return [
        DriverRaceResultRead.model_validate(row._mapping)
        for row in races_result
    ]