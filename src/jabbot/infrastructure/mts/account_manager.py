import base64
import logging

import aiohttp
import orjson

from ...core.types import MTSAccessToken


class MTSCredentials:
    def __init__(self, login: str, password: str):
        self.login = login
        self.password = password


class MTSAccountManager:
    def __init__(self, accounts: dict[str, MTSCredentials]):
        self.accounts = accounts

    def get_credentials(self, account_number: str) -> MTSCredentials:
        if account_number not in self.accounts:
            raise KeyError(f"MTS account {account_number} not found")
        return self.accounts[account_number]

    def get_all_account_numbers(self) -> list[str]:
        return list(self.accounts.keys())

    async def get_token_for_account(
        self,
        account_number: str,
    ) -> MTSAccessToken:
        credentials = self.get_credentials(account_number)
        return await self._fetch_token(credentials)

    async def _fetch_token(
        self,
        credentials: MTSCredentials,
    ) -> MTSAccessToken:

        login = credentials.login
        password = credentials.password

        async with aiohttp.ClientSession() as session:
            credentials_str = f"{login}:{password}"
            auth_base64 = base64.b64encode(
                credentials_str.encode("utf-8"),
            ).decode("utf-8")

            headers = {
                "Authorization": f"Basic {auth_base64}",
                "Content-Type": "application/x-www-form-urlencoded",
            }

            post_data = "grant_type=client_credentials"
            async with session.post(
                "https://api.mts.ru/token",
                headers=headers,
                data=post_data,
            ) as resp:
                if resp.status != 200:
                    error_text = await resp.text()
                    raise Exception(
                        f"Failed to get token: {resp.status} - {error_text}",
                    )

                response_text = await resp.text()

            try:
                resp_json = orjson.loads(response_text)
            except orjson.JSONDecodeError as e:
                logging.error(f"Failed to parse token response: {e}")
                raise Exception(f"Invalid JSON response: {e}") from e

            access_token = resp_json.get("access_token")
            if not access_token:
                error_description = resp_json.get(
                    "error_description",
                    resp_json.get("error", "Unknown error"),
                )
                raise Exception(error_description)

            return MTSAccessToken(access_token)
