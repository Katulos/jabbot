import logging
from typing import Any

from dishka.integrations.base import FromDishka

from ...client import Client
from .context import inject
from .scheduler import Scheduler


@inject
async def send_delay_message(
    scheduler: FromDishka[Scheduler],
    client: Client,
    message: dict[str, Any],
) -> None:
    logging.info(f"Sending message: {message}")
