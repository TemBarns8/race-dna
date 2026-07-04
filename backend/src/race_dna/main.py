from typing import Annotated, Literal

from fastapi import Depends, FastAPI
from pydantic import BaseModel
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from race_dna import __version__
from race_dna.database import get_db_session

from race_dna.api.routes.drivers import router as drivers_router

class HealthResponse(BaseModel):
    status: Literal["ok"]
    version: str


class ReadinessResponse(BaseModel):
    status: Literal["ready"]
    database: Literal["ok"]


DatabaseSession = Annotated[
    AsyncSession,
    Depends(get_db_session),
]


app = FastAPI(
    title="Race DNA API",
    version=__version__,
    description="Explainable Formula 1 driver analytics API.",
)

app.include_router(
    drivers_router,
    prefix="/api/v1",
)

@app.get(
    "/api/v1/health",
    response_model=HealthResponse,
    tags=["health"],
)
async def health() -> HealthResponse:
    return HealthResponse(status="ok", version=__version__)


@app.get(
    "/api/v1/health/ready",
    response_model=ReadinessResponse,
    tags=["health"],
)
async def readiness(
    session: DatabaseSession,
) -> ReadinessResponse:
    await session.execute(text("SELECT 1"))
    return ReadinessResponse(status="ready", database="ok")