import asyncio
import logging
from typing import Any

from slixmpp import JID, ClientXMPP

from .commands import CommandRegistry
from .commands.adhoc import AdhocCommandRegistry


class Client(ClientXMPP):
    def __init__(
        self,
        jid: str,
        password: str,
        resource: str,
    ) -> None:
        super().__init__(f"{jid}/{resource}", password)

        self.__jid = JID(jid)

        self.register_plugin("xep_0030")  # Service Discovery
        self.register_plugin(
            "xep_0199",
            {"keepalive": True, "frequency": 15},
        )  # Ping
        self.register_plugin("xep_0004")  # Data Forms
        self.register_plugin("xep_0045")  # Multi-User Chat
        self.register_plugin("xep_0050")  # Adhoc Commands

        self.add_event_handler("session_start", self._on_session_start)
        self.add_event_handler("disconnected", self._on_disconnected)
        self.add_event_handler("failed_auth", self._on_auth_failed)
        self.add_event_handler("socket_error", self._on_socket_error)
        self.add_event_handler("message", self._on_message)

    async def _on_session_start(self, event: dict[str, Any]) -> None:
        self.send_presence()
        self.get_roster()

        # Загружаем обычные команды
        command_registry = CommandRegistry.get_instance()
        command_registry.load_commands()

        # Загружаем Adhoc-команды
        adhoc_registry = AdhocCommandRegistry.get_instance()
        adhoc_registry.load_commands(self)

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
            response = self.make_message(
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
                await command.execute(self, msg, args)
                logging.info(f"Command /{command_name} executed by {sender}")
            except Exception as e:
                logging.error(
                    f"Error executing command /{command_name}: {e}",
                )
                error_text = f"Command execution error: {str(e)}"
                response = self.make_message(
                    mto=sender,
                    mbody=error_text,
                    mtype="chat",
                )
                response.send()


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
