import logging
from typing import Any

from . import BaseAdhocCommand


class GreetingCommand(BaseAdhocCommand):
    @property
    def node(self) -> str:
        return "greeting"

    @property
    def name(self) -> str:
        return "Greeting"

    @property
    def description(self) -> str:
        return "Send a custom greeting to a JID"

    async def execute_initial(self, iq: Any, session: dict) -> dict:
        client = session.get("_client")

        if not client:
            logging.error("Client not found in session")
            session["notes"] = [("error", "Internal error: client not found")]
            return session

        form = client["xep_0004"].make_form("form", "Greeting")
        form["instructions"] = "Send a custom greeting to a JID"
        form.add_field(
            var="greeting",
            ftype="text-single",
            label="Your greeting",
            required=True,
        )
        form.add_field(
            var="jid",
            ftype="jid-single",
            label="Recipient JID",
            required=True,
        )

        session["payload"] = form
        session["next"] = session.get("_complete_handler")
        session["has_next"] = False

        return session

    async def execute_complete(
        self,
        payload: Any,
        session: dict,
    ) -> dict | None:
        form = payload

        values = form["values"]
        greeting = values.get("greeting", "")
        recipient_jid = values.get("jid", "")

        if not greeting or not recipient_jid:
            session["notes"] = [("error", "Greeting and JID are required")]
            return session

        client = session.get("_client")
        if client:
            client.send_message(
                mto=recipient_jid,
                mbody=f"{greeting}",
                mtype="chat",
            )

            logging.info(
                f"Greeting '{greeting}' sent to user {recipient_jid}",
            )

        session["notes"] = [("info", f"Greeting sent to {recipient_jid}")]
        session["payload"] = None
        session["next"] = None

        return session

    async def execute_cancel(self, session: dict) -> dict | None:
        logging.info(
            f"Greeting command canceled by user {session.get('from')}",
        )
        return None
