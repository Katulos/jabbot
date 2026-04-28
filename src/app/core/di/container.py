from dishka import AsyncContainer, make_async_container

from .providers.client import ClientProvider


def get_async_container() -> AsyncContainer:
    providers = [
        ClientProvider(),
    ]
    container = make_async_container(*providers)

    return container
