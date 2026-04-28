import asyncio
import logging
import signal

import click

from ..api import run as run_api
from ..client import Client
from ..client import run as run_client
from ..core import logging as logger
from ..core.config import settings
from ..core.di.container import get_async_container
from ..infrastructure.scheduler.scheduler import Scheduler


@click.group()
def cli() -> None:
    """Main CLI group."""
    debug = settings.get("debug")

    if debug:
        logger.setup_logger(loglevel=logging.DEBUG)
    else:
        logger.setup_logger(loglevel=logging.INFO)


@cli.group()
def run() -> None:
    """Run application components."""
    pass


@run.command()
def api() -> None:
    """Run API server."""
    logging.info("Running API server")
    run_api()


@run.command()
def client() -> None:
    """Run XMPP client."""
    logging.info("Running XMPP client")
    asyncio.run(_run_xmpp_client())


@run.command()
def scheduler() -> None:
    """Run Scheduler."""
    logging.info("Running Scheduler")
    asyncio.run(_run_scheduler())


async def _run_scheduler() -> None:
    container = get_async_container()

    loop = asyncio.get_running_loop()

    stop_event = asyncio.Event()

    def signal_handler():
        logging.info("Received exit signal.")
        stop_event.set()

    try:
        for sig in (signal.SIGINT, signal.SIGTERM):
            loop.add_signal_handler(sig, signal_handler)
    except NotImplementedError:
        logging.warning(
            "Signal handlers not supported on this platform via add_signal_handler.",
        )

    try:
        async with container as ctx:
            await ctx.get(Scheduler)
            await stop_event.wait()
    except Exception as e:
        logging.critical(e)
    finally:
        await container.close()


async def _run_xmpp_client() -> None:
    container = get_async_container()

    client = await container.get(Client)
    stop_event = asyncio.Event()

    loop = asyncio.get_running_loop()

    def signal_handler():
        logging.info("Received exit signal.")
        stop_event.set()

    try:
        for sig in (signal.SIGINT, signal.SIGTERM):
            loop.add_signal_handler(sig, signal_handler)
    except NotImplementedError:
        logging.warning(
            "Signal handlers not supported on this platform via add_signal_handler.",
        )

    try:
        await run_client(client, stop_event)
    except Exception as e:
        logging.critical(f"Unhandled exception in main: {e}", exc_info=True)
    finally:
        await container.close()
