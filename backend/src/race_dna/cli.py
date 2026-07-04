import argparse
import asyncio

from race_dna.database import (
    async_session_factory,
    engine,
)
from race_dna.ingestion.drivers import sync_driver
from race_dna.integrations.jolpica.client import JolpicaClient


async def run_sync_driver(driver_id: str) -> None:
    try:
        async with async_session_factory() as session:
            driver, created = await sync_driver(
                session=session,
                client=JolpicaClient(),
                driver_id=driver_id,
            )

        action = "created" if created else "updated"
        print(
            f"{action}: {driver.slug}, "
            f"number={driver.permanent_number}"
        )
    finally:
        await engine.dispose()


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="race-dna",
        description="Race DNA maintenance commands.",
    )
    subparsers = parser.add_subparsers(
        dest="command",
        required=True,
    )

    sync_parser = subparsers.add_parser(
        "sync-driver",
        help="Synchronize a driver from Jolpica.",
    )
    sync_parser.add_argument("driver_id")

    args = parser.parse_args()

    if args.command == "sync-driver":
        asyncio.run(run_sync_driver(args.driver_id))


if __name__ == "__main__":
    main()