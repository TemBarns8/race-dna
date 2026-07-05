import argparse
import asyncio

from race_dna.ingestion.qualifying_results import (
    sync_driver_qualifying_results,
)
from race_dna.database import (
    async_session_factory,
    engine,
)
from race_dna.ingestion.drivers import sync_driver
from race_dna.ingestion.race_results import sync_driver_results
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


async def run_sync_results(driver_id: str) -> None:
    try:
        async with async_session_factory() as session:
            summary = await sync_driver_results(
                session=session,
                client=JolpicaClient(),
                driver_id=driver_id,
            )

        print(f"received={summary.received}")
        print(f"seasons_created={summary.seasons_created}")
        print(f"races_created={summary.races_created}")
        print(f"results_created={summary.results_created}")
        print(f"results_updated={summary.results_updated}")
    finally:
        await engine.dispose()

async def run_sync_qualifying(driver_id: str) -> None:
    try:
        async with async_session_factory() as session:
            summary = await sync_driver_qualifying_results(
                session=session,
                client=JolpicaClient(),
                driver_id=driver_id,
            )

        print(f"received={summary.received}")
        print(f"seasons_created={summary.seasons_created}")
        print(f"races_created={summary.races_created}")
        print(
            f"qualifying_created={summary.qualifying_created}"
        )
        print(
            f"qualifying_updated={summary.qualifying_updated}"
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

    sync_driver_parser = subparsers.add_parser(
        "sync-driver",
        help="Synchronize a driver from Jolpica.",
    )
    sync_driver_parser.add_argument("driver_id")

    sync_results_parser = subparsers.add_parser(
        "sync-results",
        help="Synchronize driver race results from Jolpica.",
    )
    sync_results_parser.add_argument("driver_id")

    sync_qualifying_parser = subparsers.add_parser(
        "sync-qualifying",
        help="Synchronize driver qualifying results from Jolpica.",
    )
    sync_qualifying_parser.add_argument("driver_id")

    args = parser.parse_args()

    if args.command == "sync-driver":
        asyncio.run(run_sync_driver(args.driver_id))
    elif args.command == "sync-results":
        asyncio.run(run_sync_results(args.driver_id))
    elif args.command == "sync-qualifying":
        asyncio.run(run_sync_qualifying(args.driver_id))

if __name__ == "__main__":
    main()