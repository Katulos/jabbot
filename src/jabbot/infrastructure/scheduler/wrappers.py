import logging

from dishka.integrations.base import FromDishka
from slixmpp import JID

from ..xmpp import XMPPSchedulerClient
from .context import inject


@inject
async def send_delay_message(
    client: FromDishka[XMPPSchedulerClient],
    to: str,
    message: str,
) -> None:
    client.client.send_message(mto=JID(to), mbody=message, mtype="chat")
    logging.debug(f"Sending message: {message}")
