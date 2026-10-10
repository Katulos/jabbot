from dishka import AsyncContainer, make_async_container
from dishka.integrations.fastapi import FastapiProvider

from .providers.client import ClientProvider
from .providers.fastapi_command import FastAPICommandProvider
from .providers.scheduler import SchedulerProvider


def get_async_container() -> AsyncContainer:
    providers = [
        ClientProvider(),
        SchedulerProvider(),
        #
        FastapiProvider(),
        FastAPICommandProvider(),
    ]
    container = make_async_container(*providers)

    return container
