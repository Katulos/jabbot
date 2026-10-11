from collections.abc import AsyncIterable

from dishka import AsyncContainer, Provider, Scope, provide

from ....infrastructure.xmpp import Client, XMPPClient


class ClientProvider(Provider):
    scope = Scope.APP

    @provide
    async def provide_client(
        self,
        container: AsyncContainer,
    ) -> AsyncIterable[Client]:
        async with XMPPClient(
            container=container,
        ) as client:
            yield client
