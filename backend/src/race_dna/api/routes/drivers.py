from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from race_dna.database import get_db_session
from race_dna.db.models import Driver
from race_dna.schemas.driver import DriverCreate, DriverRead


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