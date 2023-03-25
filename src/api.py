import requests
from config import API_KEY, LIMIT


def get_transactions(address):
    response = requests.get(f'https://toncenter.com/api/v2/getTransactions?address={address}&limit={LIMIT}&api_key={API_KEY}').json()
    if response['ok']:
        transactions = response['result']
        return transactions
    else:
        return []
            
def get_balance(address):
    response = requests.get(f'https://toncenter.com/api/v2/getAddressBalance?address={address}&api_key={API_KEY}').json()
    if response['ok']:
        balance = float(response['result']) / 1000000000
        return balance
    else:
        return 0