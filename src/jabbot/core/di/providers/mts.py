from dishka import Provider, Scope, from_context

from ....infrastructure.mts.account_manager import (
    MTSAccountManager,
)


class MTSAccessTokenProvider(Provider):
    scope = Scope.APP

    account_manager = from_context(
        provides=MTSAccountManager,
        scope=Scope.APP,
    )

    def provide_account_manager(
        self,
        account_manager: MTSAccountManager,
    ) -> MTSAccountManager:
        return account_manager
