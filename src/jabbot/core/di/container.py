from dishka import AsyncContainer, make_async_container
from dishka.integrations.fastapi import FastapiProvider

from ...infrastructure.mts import (
    MTSAccountManager,
    MTSCredentials,
)
from ..settings import settings
from .providers.client import ClientProvider
from .providers.fastapi_command import FastAPICommandProvider
from .providers.mts import MTSAccessTokenProvider
from .providers.scheduler import SchedulerProvider


def _create_mts_accounts() -> dict[str, MTSCredentials]:
    mts_config = settings.get("mts", {})

    if not mts_config:
        raise ValueError(
            "MTS configuration is missing. Please add 'mts' section to settings.yml",
        )

    accounts: dict[str, MTSCredentials] = {}

    for phone_number, account_config in mts_config.items():
        login = account_config.get("login")
        password = account_config.get("password")

        if not login or not password:
            raise ValueError(
                f"MTS login and password must be specified for account {phone_number}",
            )

        accounts[str(phone_number)] = MTSCredentials(
            login=str(login),
            password=str(password),
        )

    if not accounts:
        raise ValueError("No valid MTS accounts configured in settings")

    return accounts


def get_async_container() -> AsyncContainer:
    accounts = _create_mts_accounts()
    account_manager = MTSAccountManager(accounts)

    providers = [
        ClientProvider(),
        SchedulerProvider(),
        #
        FastapiProvider(),
        FastAPICommandProvider(),
        #
        MTSAccessTokenProvider(),
    ]
    container = make_async_container(
        *providers,
        context={MTSAccountManager: account_manager},
    )

    return container
