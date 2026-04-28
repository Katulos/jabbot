import asyncio
import logging
from contextlib import suppress

import click
from dishka import AsyncContainer

from ..api import run_api
from ..client import Client
from ..core import logging as logger
from ..core.config import settings
from ..core.di.container import get_async_container


@click.group()
def cli() -> None:
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
    asyncio.run(run_client())


async def run_client() -> None:

    container: AsyncContainer | None = None
    client: Client | None = None
    client_task: asyncio.Task | None = None

    try:
        container = get_async_container()

        client = await container.get(Client)

        client.connect()

        client_task = asyncio.create_task(asyncio.sleep(0))

        logging.info("XMPP Bot is running. Press Ctrl+C to exit.")

        stop_event = asyncio.Event()

        try:
            await stop_event.wait()
        except asyncio.CancelledError:
            logging.info("Shutdown signal received (CancelledError).")

    except KeyboardInterrupt:
        logging.info("KeyboardInterrupt caught directly.")
    except Exception as e:
        logging.critical(e)
        raise
    finally:
        logging.info("Starting graceful shutdown...")

        if client_task and not client_task.done():
            client_task.cancel()
            with suppress(asyncio.CancelledError):
                await client_task

        if client:
            try:
                client.disconnect()
                logging.info("XMPP Client disconnected.")
            except RuntimeError as e:
                if "Event loop is closed" in str(e):
                    logging.info(
                        "Loop closed during client disconnect. Ignored.",
                    )
                else:
                    logging.error(f"Error during client disconnect: {e}")
            except Exception as e:
                logging.error(
                    f"Unexpected error during client disconnect: {e}",
                )

        if container:
            try:
                loop = asyncio.get_running_loop()
                if not loop.is_closed():
                    await container.close()
                    logging.info("DI Container closed successfully.")
                else:
                    logging.warning(
                        "Event loop is closed. Skipping container close.",
                    )
            except RuntimeError as e:
                if "Event loop is closed" in str(e):
                    logging.info(
                        "Loop closed during container close. Ignored.",
                    )
                else:
                    logging.error(f"Error closing DI container: {e}")
            except Exception as e:
                logging.error(f"Unexpected error closing DI container: {e}")

        logging.info("Application shutdown complete.")
