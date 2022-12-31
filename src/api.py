import requests


def getTransactions():
    params = {
        'perPage': '2000',
        'currentPage': '1',
        'types[0]': 'sale',
        'types[1]': 'transfer',
    }

    response = requests.get(
        'https://ton.diamonds/api/v1/collections/annihilation/transactions',
        params=params,
    )

    return response.json()['data']['rows']


if __name__ == '__main__':
    print(len(getTransactions()))
