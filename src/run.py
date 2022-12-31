from pyvis.network import Network
import ast
from api import getTransactions
import datetime


def processRawTransactions(rawTransactions):
    nftAmountData = {}
    transactionsData = {}

    for rawTransaction in rawTransactions:
        addressFrom = rawTransaction['from']
        addressTo = rawTransaction['to']

        usernameFrom = '' if not (
            'fromUser' in rawTransaction and 'username' in rawTransaction['fromUser']
        ) else rawTransaction['fromUser']['username']

        usernameTo = '' if not (
            'toUser' in rawTransaction and 'username' in rawTransaction['toUser']
        ) else rawTransaction['toUser']['username']

        transactionType = rawTransaction['transactionType']

        nftAmountData[addressTo] = 1 if addressTo not in nftAmountData \
            else nftAmountData[addressTo] + 1

        nftAmountData[addressFrom] = -1 if addressFrom not in nftAmountData \
            else nftAmountData[addressFrom] - 1

        transactionData = [
            (addressFrom, usernameFrom),
            (addressTo, usernameTo),
            transactionType
        ]

        transactionsData[str(transactionData)] = 1 if str(transactionData) not in transactionsData \
            else transactionsData[str(transactionData)] + 1
    return transactionsData, nftAmountData


def createGraph(transactionsData, nftAmountData):
    G = Network(height="750px", width="100%", bgcolor="#222222",
                font_color="white", directed=True)

    for transaction, amount in transactionsData.items():
        (addressFrom, usernameFrom), (addressTo,
                                      usernameTo), transactionType = ast.literal_eval(transaction)

        amountFrom = nftAmountData[addressFrom]
        amountTo = nftAmountData[addressTo]

        fromLabel = f'[{amountFrom}] ' + usernameFrom\
            if usernameFrom \
            else f'({amountFrom}) ' + addressFrom[:3] + '...' + addressFrom[-3:]

        toLabel = f'[{amountTo}] ' + usernameTo \
            if usernameTo \
            else f'({amountTo}) ' + \
            addressTo[:3] + '...' + addressTo[-3:]

        fromColor = '#0088CC' if amountFrom else '#8C8C8C'
        toColor = '#0088CC' if amountTo else '#8C8C8C'

        G.add_node(addressFrom, label=fromLabel, title=addressFrom,
                   value=amountFrom, color=fromColor)
        G.add_node(addressTo, label=toLabel, title=addressTo,
                   value=amountTo, color=toColor)

        if transactionType == 'sale':
            G.add_edge(addressFrom, addressTo, value=amount,
                       color='red', title=amount)
        elif transactionType == 'transfer':
            G.add_edge(addressFrom, addressTo, value=amount,
                       color='green', title=amount)

    return G


if __name__ == '__main__':
    rawTransactions = getTransactions()
    transactionsData, nftAmountData = processRawTransactions(rawTransactions)

    G = createGraph(transactionsData, nftAmountData)

    direcroty = './html/'
    fileName = 'graph_' + datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S") + '.html'

    G.show(direcroty + fileName)
