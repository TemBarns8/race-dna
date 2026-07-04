import httpx2

from race_dna import __version__
from race_dna.config import get_settings
from race_dna.integrations.jolpica.schemas import (
    JolpicaDriver,
    JolpicaDriverResponse,
)


class JolpicaDriverNotFoundError(LookupError):
    pass


class JolpicaClient:
    def __init__(
        self,
        base_url: str | None = None,
        timeout_seconds: float | None = None,
    ) -> None:
        settings = get_settings()

        selected_base_url = (
            base_url
            if base_url is not None
            else settings.jolpica_base_url
        )
        self._base_url = f"{selected_base_url.rstrip('/')}/"
        self._timeout_seconds = (
            timeout_seconds
            if timeout_seconds is not None
            else settings.jolpica_timeout_seconds
        )

    async def get_driver(
        self,
        driver_id: str,
    ) -> JolpicaDriver:
        async with httpx2.AsyncClient(
            base_url=self._base_url,
            timeout=self._timeout_seconds,
            headers={"User-Agent": f"race-dna/{__version__}"},
        ) as client:
            response = await client.get(
                f"drivers/{driver_id}.json"
            )
            response.raise_for_status()

        parsed = JolpicaDriverResponse.model_validate(
            response.json()
        )
        drivers = parsed.mr_data.driver_table.drivers

        if not drivers:
            raise JolpicaDriverNotFoundError(
                f"Jolpica driver '{driver_id}' was not found."
            )

        return drivers[0]