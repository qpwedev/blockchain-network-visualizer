from datetime import datetime

from pyvis.network import Network
from tonsdk.utils import Address

from api import getTransactions


def process_raw_transactions(transactions):
    transactions_data = []

    for transaction in transactions:

        addressFrom, usernameFrom, addressTo, usernameTo, value = '', '', '', '', 0
        transactionType = True if len(transaction['out_msgs']) != 0 else False
        unixDate = transaction['utime']

        transaction = transaction['out_msgs'][0] if transactionType else transaction['in_msg']

        if 'source' in transaction:
            addressFrom = Address(transaction['source']['address']).to_string(True, True, True)
        else:
            continue
        if 'name' in transaction['source']:
            usernameFrom = transaction['source']['name']

        if 'destination' in transaction:
            addressTo = Address(transaction['destination']['address']).to_string(True, True, True)
        else:
            continue
        if 'name' in transaction['destination']:
            usernameTo = transaction['destination']['name']

        value = str(transaction['value'] / 10e9) + " TON"
        date = datetime.utcfromtimestamp(unixDate).strftime('%Y-%m-%d %H:%M')

        transaction = [
            addressFrom, usernameFrom,
            addressTo, usernameTo,
            transactionType, value, date
        ]

        transactions_data.append(transaction)
    return transactions_data


def create_graph(transactions_data):
    G = Network(height="100vh", width="100%", bgcolor="#222222",
                font_color="white", directed=True)

    for transaction in transactions_data:

        addressFrom = transaction[0]
        usernameFrom = transaction[1]
        addressTo = transaction[2]
        usernameTo = transaction[3]
        transactionType = transaction[4]
        value = transaction[5]
        date = transaction[6]

        fromLabel = usernameFrom if usernameFrom else addressFrom[:3] + '...' + addressFrom[-3:]
        toLabel = usernameTo if usernameTo else addressTo[:3] + '...' + addressTo[-3:]

        try:
            fromNode = G.get_node(addressFrom)
            fromNode['title'] += f'\n\nTo: {addressTo}\nValue: {value} // {date}'
        except Exception:
            pass
        finally:
            fromTitle = f'{usernameFrom if usernameFrom else addressFrom}\n' \
                        f'\nTo: {addressTo}\nValue: {value} // {date}'

        try:
            toNode = G.get_node(addressTo)
            toNode['title'] += f'\n\nFrom: {addressFrom}\nValue: {value} // {date}'
        except Exception:
            pass
        finally:
            toTitle = f'{usernameTo if usernameTo else addressTo}\n' \
                      f'\nFrom: {addressFrom}\nValue: {value} // {date}'

        fromColor = '#0088CC' if usernameFrom else '#8C8C8C'
        toColor = '#0088CC' if usernameTo else '#8C8C8C'

        G.add_node(addressFrom, label=fromLabel, title=fromTitle, color=fromColor, value=value)
        G.add_node(addressTo, label=toLabel, title=toTitle, color=toColor, value=value)

        arr_edges = G.get_edges()
        inner_array = False
        for item in arr_edges:
            if item['from'] == addressFrom and item['to'] == addressTo:
                inner_array = True
                break

        if not inner_array:

            amount = 0
            for i in transactions_data:
                if i[0] == addressFrom and i[2] == addressTo and i[4] == transactionType:
                    amount += 1

            if transactionType:
                G.add_edge(addressFrom, addressTo, value=amount,
                           color='red', title=amount)
            elif not transactionType:
                G.add_edge(addressFrom, addressTo, value=amount,
                           color='green', title=amount)
    return G


if __name__ == '__main__':
    address = 'address'  # адрес нужного кошелька
    count = 200  # количество последних транзакций

    transactions = getTransactions(address, count)
    transactions_data = process_raw_transactions(transactions)
    G = create_graph(transactions_data)

    G.set_options('''{
        "physics": {
            "forceAtlas2Based": {
                "springLength": 200
            },
            "minVelocity": 0.75,
            "solver": "forceAtlas2Based"
        }
    }''')

    G.show('test.html')
