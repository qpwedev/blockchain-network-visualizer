import asyncio
from typing import List
import httpx
from config import everspaceCenterConfig, ApiConfig, DEPTH


class EverspaceCenterApi:
    """
    A class to interact with the Everspace Center API.
    https://everspace.center/toncoin
    """

    def __init__(self, config: ApiConfig):
        self.config = config

    async def get_transactions(self, address: str) -> List[dict]:
        """
        Get transactions for a given address asynchronously.
        :param address: The address for which to fetch the transactions.
        :return: A list of transactions if successful, an empty list otherwise.
        """
        headers = {
            'X-API-KEY': self.config.api_key,
        }
        params = {
            'address': address,
            'limit': DEPTH,
        }

        for _ in range(self.config.retries):
            try:
                async with httpx.AsyncClient() as client:
                    response = await client.get(
                        'https://everspace.center/toncoin/getTransactions',
                        params=params, headers=headers, timeout=self.config.timeout
                    )
                    response_json = response.json()

                    if response.status_code == 200:
                        return response_json

                    await asyncio.sleep(self.config.delay)
            except httpx.HTTPError:
                await asyncio.sleep(self.config.delay)

        return []

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
                        return balance

                    await asyncio.sleep(self.config.delay)
            except httpx.HTTPError:
                await asyncio.sleep(self.config.delay)

        return 0


async def main():
    addresses = [
        'EQDo8eYrFypI4cCZures4CiGsPXZyyHKR9-f6Vxly60h5lrh',
        'EQDo8eYrFypI4cCZures4CiGsPXZyyHKR9-f6Vxly60h5lrh'
    ]

    api = EverspaceCenterApi(everspaceCenterConfig)

    for address in addresses:
        transactions = await api.get_transactions(address)
        balance = await api.get_balance(address)
        print(len(transactions), f'transactions for {address}')
        print(f'Balance for {address}: {balance}')


if __name__ == '__main__':
    asyncio.run(main())
