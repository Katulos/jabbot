import logging

import click

from ..core import logging as logger
from ..core.config import settings

logger.setup_logger()

@click.group()
def cli() -> None:
    pass

@cli.command()
def start() -> None:
    debug = settings.get("debug")

    if debug:
        logger.setup_logger(loglevel=logging.DEBUG)
    else:
        logger.setup_logger(loglevel=logging.INFO)

    click.echo("Hello world")