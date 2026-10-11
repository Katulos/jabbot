import logging
from typing import cast

from slixmpp import ClientXMPP

from ....core.di.container import get_async_container
from ....infrastructure.mts import MTSAccountManager, get_account_balance
from . import BaseCommand


class BalanceCommand(BaseCommand):
    @property
    def name(self) -> str:
        return "balance"

    @property
    def description(self) -> str:
        return "Show MTS Balance. Usage: /balance"

    @property
    def aliases(self) -> list:
        return ["bal"]

    async def execute(
        self,
        client: ClientXMPP,
        msg: dict,
        args: str,
    ) -> None:
        logging.info(f"Executing balance command for user {msg['from']}")

        sender = msg["from"]
        account_manager = None

        try:
            container = get_async_container()
            account_manager = await container.get(MTSAccountManager)
            balances = []
            for account in account_manager.get_all_account_numbers():
                try:
                    access_token = (
                        await account_manager.get_token_for_account(
                            account,
                        )
                    )
                    balance = await get_account_balance(
                        access_token,
                        cast(int, account),
                    )
                    balances.append(f"{account}: {balance}")
                except Exception as e:
                    logging.exception(
                        f"Failed to get balance for {account}: {e}",
                    )
                    balances.append(f"{account}: Error - {str(e)}")

            body = "MTS Balances:\n" + "\n".join(balances)

        except KeyError as e:
            logging.error(f"Account not found: {e}")
            available = (
                ", ".join(account_manager.get_all_account_numbers())
                if account_manager is not None
                else "unknown"
            )
            body = (
                f"Error: Account not found. Available accounts: {available}"
            )
        except Exception as e:
            logging.error(f"Failed to get balance: {e}")
            body = f"Error getting balance: {str(e)}"

        response = client.make_message(mto=sender, mbody=body)
        response.send()

        logging.info(f"Balance sent to user {sender}")
