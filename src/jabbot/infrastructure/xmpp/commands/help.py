import logging

from slixmpp import ClientXMPP

from . import BaseCommand, CommandRegistry


class HelpCommand(BaseCommand):
    @property
    def name(self) -> str:
        return "help"

    @property
    def description(self) -> str:
        return "Show list of available commands"

    @property
    def aliases(self) -> list:
        return ["h", "?"]

    async def execute(self, client: ClientXMPP, msg: dict, args: str) -> None:
        registry = CommandRegistry.get_instance()
        help_text = registry.get_help_text()

        sender = msg["from"]

        response = client.make_message(
            mto=sender,
            mbody=help_text,
            mtype="chat",
        )
        response.send()

        logging.info(f"Help sent to user {sender}")
