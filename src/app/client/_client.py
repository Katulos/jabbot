import asyncio
import logging
from typing import Any

from slixmpp import ClientXMPP


class Client(ClientXMPP):
    def __init__(
        self,
        jid: str,
        password: str,
        resource: str,
    ) -> None:
        super().__init__(f"{jid}/{resource}", password)

        self.register_plugin("xep_0030")  # Service Discovery
        self.register_plugin("xep_0199")  # Ping
        self.register_plugin("xep_0004")  # Data Forms
        self.register_plugin("xep_0050")  # Adhoc Commands

        self.add_event_handler("session_start", self._on_session_start)
        self.add_event_handler("disconnected", self._on_disconnected)
        self.add_event_handler("failed_auth", self._on_auth_failed)
        self.add_event_handler("socket_error", self._on_socket_error)
        self.add_event_handler("message", self._on_message)

    async def _on_session_start(self, event: dict[str, Any]) -> None:
        self.send_presence()
        self.get_roster()
        logging.info("Session started")

    async def _on_disconnected(self, event: dict[str, Any]) -> None:
        logging.info("Disconnected")

    async def _on_auth_failed(self, event: dict[str, Any]) -> None:
        logging.error("Authentication failed")
        self.disconnect()

    async def _on_socket_error(self, event: dict[str, Any]) -> None:
        logging.error("Socket error")
        self.disconnect()

    async def _on_message(self, msg):
        if msg["type"] in ("chat", "normal"):
            msg.reply("Thanks for sending\n{body}".format(**msg)).send()


async def run(client: Client, stop_event: asyncio.Event) -> None:
    try:
        client.connect()
    except Exception as e:
        logging.error(e)

    tasks = [
        asyncio.create_task(stop_event.wait()),
    ]

    try:
        done, pending = await asyncio.wait(
            tasks,
            return_when=asyncio.FIRST_COMPLETED,
        )

        for task in pending:
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass

    except asyncio.CancelledError:
        pass
    finally:
        client.disconnect()

        await asyncio.sleep(1)
