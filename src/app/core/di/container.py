from dishka import AsyncContainer, make_async_container

from .providers.client import ClientProvider
from .providers.scheduler import SchedulerProvider


def get_async_container() -> AsyncContainer:
    providers = [
        ClientProvider(),
        SchedulerProvider(),
    ]
    container = make_async_container(*providers)

    return container
