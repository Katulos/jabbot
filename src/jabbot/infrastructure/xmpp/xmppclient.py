import logging
from typing import Any

from dishka import AsyncContainer
from slixmpp import ClientXMPP
from slixmpp.exceptions import IqError, IqTimeout

from ...core.settings import settings
from .commands import CommandRegistry
from .commands.adhoc import AdhocCommandRegistry
from .context import XMPPClientContext
from .protocol import Client


class XMPPClient(Client):
    def __init__(self, container: AsyncContainer) -> None:

        XMPPClientContext.container = container

        self.container = container

        jid = settings.get("xmpp.jid")
        password = settings.get("xmpp.password")
        resource = settings.get("xmpp.resource", "bot")

        self.client = ClientXMPP(
            f"{jid}/{resource}",
            password,
        )

    async def _on_session_start(self, event: dict[str, Any]) -> None:
        try:
            await self.client.get_roster()
        except IqError as err:
            logging.error("Error: {}".format(err.iq["error"]["condition"]))
        except IqTimeout:
            logging.error("Error: Request timed out")
        self.client.send_presence()

        command_registry = CommandRegistry.get_instance()
        command_registry.load_commands()

        adhoc_registry = AdhocCommandRegistry.get_instance()
        adhoc_registry.load_commands(self.client)

        logging.debug("XMPP Client session started")

    async def _on_disconnected(self, event: dict[str, Any]) -> None:
        logging.debug("XMPP Client disconnected")

    async def _on_auth_failed(self, event: dict[str, Any]) -> None:
        logging.error("XMPP Client authentication failed")
        self.client.disconnect()

    async def _on_socket_error(self, event: dict[str, Any]) -> None:
        logging.error("XMPP Client socket error")
        self.client.disconnect()

    async def _on_message(self, msg):

        body = msg.get("body", "")

        if not body:
            return

        logging.debug("Got message: {}".format(str(body).replace("\n", " ")))

        if body.startswith("/"):
            await self._handle_command(msg, body)

    async def _handle_command(self, msg: dict, body: str) -> None:
        parts = body.strip().split(maxsplit=1)
        command_name = parts[0][1:]
        args = parts[1] if len(parts) > 1 else ""

        registry = CommandRegistry.get_instance()

        command = registry.get_command(command_name)

        sender = msg["from"]

        if command is None:
            error_text = f"Unknown command: /{command_name}\nType /help for list of commands"
            response = self.client.make_message(
                mto=sender,
                mbody=error_text,
                mtype="chat",
            )
            response.send()
            logging.warning(
                f"Unknown command from {sender}: /{command_name}",
            )
        else:
            try:
                await command.execute(self.client, msg, args)
                logging.info(f"Command /{command_name} executed by {sender}")
            except Exception as e:
                logging.error(
                    f"Error executing command /{command_name}: {e}",
                )
                error_text = f"Command execution error: {str(e)}"
                response = self.client.make_message(
                    mto=sender,
                    mbody=error_text,
                    mtype="chat",
                )
                response.send()

    async def start(self) -> None:
        self.client.register_plugin("xep_0030")  # Service Discovery
        self.client.register_plugin(
            "xep_0199",
            {"keepalive": True, "frequency": 15},
        )  # Ping
        self.client.register_plugin("xep_0004")  # Data Forms
        self.client.register_plugin("xep_0045")  # Multi-User Chat
        self.client.register_plugin("xep_0050")  # Adhoc Commands

        self.client.add_event_handler("session_start", self._on_session_start)
        self.client.add_event_handler("disconnected", self._on_disconnected)
        self.client.add_event_handler("failed_auth", self._on_auth_failed)
        self.client.add_event_handler("socket_error", self._on_socket_error)
        self.client.add_event_handler("message", self._on_message)
        await self.client.connect()

    async def close(self) -> None:
        self.client.disconnect()


class XMPPSchedulerClient(Client):
    def __init__(self, container: AsyncContainer) -> None:

        XMPPClientContext.container = container

        self.container = container

        jid = settings.get("xmpp.jid")
        password = settings.get("xmpp.password")
        resource = settings.get("xmpp.resource", "scheduler")

        self.client = ClientXMPP(
            f"{jid}/{resource}",
            password,
        )

    async def _on_session_start(self, event: dict[str, Any]) -> None:
        try:
            await self.client.get_roster()
            self.client.send_presence()
        except IqError as err:
            logging.error("Error: {}".format(err.iq["error"]["condition"]))
        except IqTimeout:
            logging.error("Error: Request timed out")
        finally:
            await self.client.disconnect()

    async def _on_disconnected(self, event: dict[str, Any]) -> None:
        logging.debug("Scheduler XMPP Client disconnected")

    async def _on_auth_failed(self, event: dict[str, Any]) -> None:
        logging.error("Scheduler XMPP Client authentication failed")
        self.client.disconnect()

    async def _on_socket_error(self, event: dict[str, Any]) -> None:
        logging.error("Scheduler XMPP Client socket error")
        self.client.disconnect()

    async def start(self) -> None:
        self.client.add_event_handler("session_start", self._on_session_start)
        self.client.add_event_handler("disconnected", self._on_disconnected)
        self.client.add_event_handler("failed_auth", self._on_auth_failed)
        self.client.add_event_handler("socket_error", self._on_socket_error)
        await self.client.connect()

    async def close(self) -> None:
        await self.client.disconnect()
