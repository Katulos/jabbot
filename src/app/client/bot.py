import asyncio
import logging
from typing import Any

from slixmpp import ClientXMPP

from app.core.config import settings


class EchoBot(ClientXMPP):
    def __init__(
        self,
        jid: str,
        password: str,
        resource: str,
    ) -> None:
        super().__init__(f"{jid}/{resource}", password)

        self.add_event_handler("session_start", self._on_session_start)
        self.add_event_handler("disconnected", self._on_disconnected)
        self.add_event_handler("failed_auth", self._on_auth_failed)
        self.add_event_handler("socket_error", self._on_socket_error)
        self.add_event_handler("cert_verify_failed", self._on_cert_failed)
        self.add_event_handler("message", self._message)

    async def _on_session_start(self, event: dict[str, Any]) -> None:
        self.send_presence()
        await self.get_roster()
        logging.info("Session started")

    async def _on_disconnected(self, event: dict[str, Any]) -> None:
        logging.info("Disconnected")

    async def _on_auth_failed(self, event: dict[str, Any]) -> None:
        logging.info("Authentication failed")
        self.disconnect()

    async def _on_socket_error(self, event: dict[str, Any]) -> None:
        logging.info("Socket error")
        self.disconnect()

    async def _on_cert_failed(self, event: dict[str, Any]) -> None:
        logging.info("Certificate verification failed")
        self.disconnect()

    async def _message(self, msg):
        if msg["type"] in ("chat", "normal"):
            msg.reply("Thanks for sending\n{body}".format(**msg)).send()


def run() -> None:
    jid = settings.get("xmpp_jid")
    password = settings.get("xmpp_password")
    resource = settings.get("xmpp_resource")

    client = EchoBot(jid, password, resource)

    client.register_plugin("xep_0030")  # Service Discovery
    client.register_plugin("xep_0199")  # Ping
    client.register_plugin("xep_0004")  # Data Forms
    client.register_plugin("xep_0050")  # Adhoc Commands

    try:
        client.connect()
        asyncio.get_event_loop().run_forever()
        logging.info("Connected")
    except Exception as e:
        logging.critical(e)
        raise
    except KeyboardInterrupt:
        client.disconnect()
    finally:
        client.disconnect()
        logging.info("Disconnected")
