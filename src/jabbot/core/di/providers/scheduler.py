from collections.abc import AsyncIterable

from dishka import AsyncContainer, Provider, Scope, provide

from ....infrastructure.scheduler import ApScheduler, Scheduler
from ....infrastructure.xmpp import Client


class SchedulerProvider(Provider):
    scope = Scope.APP

    @provide
    async def provide_scheduler(
        self,
        container: AsyncContainer,
        client: Client,
    ) -> AsyncIterable[Scheduler]:
        async with ApScheduler(
            container=container,
            client=client,
        ) as scheduler:
            yield scheduler
