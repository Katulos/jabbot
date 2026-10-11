import aiohttp


async def get_account_balance(token: str, account: int) -> str:
    async with aiohttp.ClientSession() as session:
        headers = {
            "Accept": "application/json",
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }

        async with session.get(
            f"https://api.mts.ru/b2b/v1/Bills/CheckBalanceByAccount?accountNo={account}",
            headers=headers,
        ) as resp:
            if resp.status != 200:
                error_text = await resp.text()
                raise Exception(
                    f"Failed to get balance: {resp.status} - {error_text}",
                )

            data = await resp.json()

            if not isinstance(data, list) or len(data) == 0:
                raise Exception(
                    "Invalid response format: expected non-empty list",
                )

            first_account = data[0]

            if "customerAccountBalance" not in first_account:
                raise Exception(
                    "customerAccountBalance not found in response",
                )

            customer_account_balance = first_account["customerAccountBalance"]

            if (
                not isinstance(customer_account_balance, list)
                or len(customer_account_balance) == 0
            ):
                raise Exception(
                    "customerAccountBalance is empty or not a list",
                )

            balance_info = customer_account_balance[0]

            if "remainedAmount" not in balance_info:
                raise Exception("remainedAmount not found in balance info")

            remained_amount = balance_info["remainedAmount"]

            if "amount" not in remained_amount:
                raise Exception("amount not found in remainedAmount")

            amount = remained_amount["amount"]

            unit = remained_amount.get("unitOfMeasure", "")

            if unit:
                return f"{amount} {unit}"
            else:
                return str(amount)
