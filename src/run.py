from pyvis.network import Network
import ast
from api import get_transactions, get_balance
import datetime


def process_transactions(transactions):
    transactions_data = {}

    for transaction in transactions:
        address_from = transaction['in_msg']['source']
        address_to = transaction['in_msg']['destination']

        transaction_type = 'transfer'
        amount = int(transaction['in_msg']['value'])

        transaction_data = [
            address_from,
            address_to,
            transaction_type
        ]

        if str(transaction_data) not in transactions_data:
            transactions_data[str(transaction_data)] = amount
        else:
            transactions_data[str(transaction_data)] += amount

    return transactions_data, {}


def create_graph(transactions_data, addresses):
    G = Network(height="750px", width="100%", bgcolor="#222222",
                font_color="white", directed=True)

    for i, address in enumerate(addresses):
        balance = get_balance(address)

        label = f'({balance}) ' + address[:3] + '...' + address[-3:]
        if address == start:
            color = '#8800CC'
        else:
            color = '#0088CC'

        G.add_node(address, label=label, title=address,
                   value=get_balance(address), color=color)
        print(f'{i}/{len(addresses)}')

    for i, (transaction, amount) in enumerate(transactions_data.items()):
        address_from, address_to, transaction_type = ast.literal_eval(transaction)
        if transaction_type == 'transfer':
            G.add_edge(address_from, address_to, value=amount,
                    color='green', title=amount)
        print(f'{i}/{len(transactions_data)}')

    return G

def sum_dictionaries(dict_1: dict, dict_2: dict):
    result = dict_1
    for key in dict_2.keys():
        if key not in result:
            result[key] = dict_2[key]
        else:
            result[key] += result[key]
            
    return result


if __name__ == '__main__':
    start = input('Enter address: ')
    addresses = [start]
    ready = []
    full_transactions_data = {}
    for i in range(int(input('Amount of steps: '))):
        new = []
        for i, address in enumerate(addresses):
            print(f'{i + 1}/{len(addresses)}')
            if address not in ready:
                raw_transactions = get_transactions(address)
                transactions_data, nftAmountData = process_transactions(raw_transactions)
                for transaction in transactions_data:
                    transaction = eval(transaction)
                    new = new + [transaction[0], transaction[1]]
                full_transactions_data = sum_dictionaries(full_transactions_data, transactions_data)
                ready.append(address)
        
        addresses = list(set(new))
    print('Visualizing..')
    G = create_graph(full_transactions_data, addresses)

    direcroty = './html/'
    fileName = 'graph_' + datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S") + '.html'

    G.show(direcroty + fileName)
    print('Ready.')
