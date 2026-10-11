from collections.abc import AsyncIterable

from dishka import AsyncContainer, Provider, Scope, provide

from ....infrastructure.scheduler import ApScheduler, Scheduler


class SchedulerProvider(Provider):
    scope = Scope.APP

    @provide
    async def provide_scheduler(
        self,
        container: AsyncContainer,
    ) -> AsyncIterable[Scheduler]:
        async with ApScheduler(
            container=container,
        ) as scheduler:
            yield scheduler
