import asyncio
import math
from typing import List
import httpx
from config import ApiConfig


class EverspaceCenterApi:
    """
    A class to interact with the Everspace Center API.
    https://everspace.center/toncoin
    """

    def __init__(self, config: ApiConfig):
        self.config = config

    async def get_transactions(self, address: str, limit: int) -> List[dict]:
        """
        Get transactions for a given address asynchronously.
        :param address: The address for which to fetch the transactions.
        :param limit: The maximum number of transactions to fetch.
        :return: A list of transactions if successful, an empty list otherwise.
        """

        headers = {
            'X-API-KEY': self.config.api_key,
        }

        max_limit = 50
        num_requests = math.ceil(limit / max_limit)

        all_transactions = []

        for _ in range(num_requests):
            params = {
                'address': address,
                'limit': max_limit,
            }

            if all_transactions:
                params['lt'] = all_transactions[-1]['lt']

            for _ in range(self.config.retries):
                try:
                    async with httpx.AsyncClient() as client:
                        response = await client.get(
                            'https://everspace.center/toncoin/getTransactions',
                            params=params, headers=headers, timeout=self.config.timeout
                        )
                        response_json = response.json()

                        if response.status_code == 200:
                            # Extract the "result" field containing the transactions
                            all_transactions.extend(response_json)

                            if len(response_json) < max_limit:
                                break

                        else:
                            await asyncio.sleep(self.config.delay)
                except httpx.HTTPError:
                    await asyncio.sleep(self.config.delay)

        if len(all_transactions) > limit:
            # Return only the requested number of transactions
            return all_transactions[:limit]
        else:
            return all_transactions

    async def get_balance(self, address: str) -> float:
        """
        Get the balance for a given address asynchronously.
        :param address: The address for which to fetch the balance.
        :return: The balance if successful, 0 otherwise.
        """
        headers = {
            'X-API-KEY': self.config.api_key,
        }
        params = {
            'address': address,
        }

        for _ in range(self.config.retries):
            try:
                async with httpx.AsyncClient() as client:
                    response = await client.get(
                        'https://everspace.center/toncoin/getBalance',
                        params=params, headers=headers, timeout=self.config.timeout
                    )
                    response_json = response.json()
                    if response.status_code == 200:
                        balance = int(response_json['balance'])
                        return balance / 1e9

                    await asyncio.sleep(self.config.delay)
            except httpx.HTTPError:
                await asyncio.sleep(self.config.delay)

        return 0
