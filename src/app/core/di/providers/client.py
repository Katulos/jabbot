import logging

from dishka import Provider, Scope, provide

from ....client import Client
from ...config import settings


class ClientProvider(Provider):
    scope = Scope.APP

    @provide
    async def provide_client(self) -> Client:
        try:
            jid = settings.get("xmpp_jid")
            password = settings.get("xmpp_password")
            resource = settings.get("xmpp_resource")
            client = Client(jid, password, resource)
            return client
        except Exception as e:
            logging.exception(e)
