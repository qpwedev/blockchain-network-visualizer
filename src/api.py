import requests


def getTransactions(address, count):
    params = {
        'limit': f'{count}'
    }

    response = requests.get(
        'https://tonapi.io/v1/blockchain/getTransactions?account=' + address,
        params=params,
    )

    return response.json()['transactions']
