from typing import Literal

from fastapi import FastAPI
from pydantic import BaseModel

from race_dna import __version__


class HealthResponse(BaseModel):
    status: Literal["ok"]
    version: str


app = FastAPI(
    title="Race DNA API",
    version=__version__,
    description="Explainable Formula 1 driver analytics API.",
)


@app.get(
    "/api/v1/health",
    response_model=HealthResponse,
    tags=["health"],
)
async def health() -> HealthResponse:
    return HealthResponse(status="ok", version=__version__)