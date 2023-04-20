import json
import asyncio
import os
from tqdm import tqdm
from typing import List, Dict, Tuple
from pyvis.network import Network
from config import EVERSPACE_CENTER_CONFIG, TX_LIMIT, DEPTH
from api.everspace_center_api import EverspaceCenterApi
import logging

SUSPICIUS_ADDRESSES = []


class Transaction:
    def __init__(self, id: str, address_from: str, address_to: str, value: int, type: str):
        self.id = id
        self.address_from = address_from
        self.address_to = address_to
        self.value = value / 1e9
        self.type = type


def parse_raw_tx(tx):
    if abs(int(tx['total_fees'])) == abs(int(tx['balance_delta'])):
        return

    tx_raw = {
        'id': tx['id'],
        'address_from': tx['in_message']['src'] if tx['in_message']['src'] else tx['in_message']['dst'],
        'address_to': tx['in_message']['dst'],
        'value':  int(tx['out_messages'][0]['value']) if tx['out_messages'] else int(tx['in_message']['value']),
        'type': 'out' if tx['out_messages'] else 'in',
    }

    tx = Transaction(
        id=tx_raw['id'],
        address_from=tx_raw['address_from'],
        address_to=tx_raw['address_to'],
        value=tx_raw['value'],
        type=tx_raw['type'],
    )

    if tx.address_from == tx.address_to:
        return

    return tx


def process_raw_txs(transactions: List[Dict]) -> Tuple[Dict, Dict]:
    txs = [
        parse_raw_tx(tx)
        for tx in transactions
        if parse_raw_tx(tx)
    ]

    return txs


def configure_network():
    net = Network(height="750px", width="100%", bgcolor="#222222",
                  font_color="white", directed=True)

    options = {
        'physics': {
            'solver': 'forceAtlas2Based',
            'forceAtlas2Based': {
                'gravitationalConstant': -100,
                'centralGravity': 0.01,
                'springLength': 200,
                'springConstant': 0.05,
                'damping': 0.4,
                'avoidOverlap': 1
            },
            'minVelocity': 0.75,
            'timestep': 0.5
        },
        'nodes': {
            'shape': 'dot',
            'scaling': {
                'min': 10,
                'max': 30
            }
        }
    }

    options_json = json.dumps(options)

    net.set_options(options_json)

    net.show('network.html')

    return net


async def fetch_balance(address, everspaceCenterApi):
    return address, await everspaceCenterApi.get_balance(address)


async def create_graph(txs: Dict, addresses: List[str], everspaceCenterApi: EverspaceCenterApi, initial_address: str) -> Network:
    net = configure_network()

    # Parallelize balance fetching
    tasks = [asyncio.create_task(fetch_balance(
        address, everspaceCenterApi)) for address in addresses]
    results = await asyncio.gather(*tasks)

    for address, balance in tqdm(results):
        label = f'({balance:.2f}) ' + address[:3] + '...' + address[-3:]

        color = '#0088CC'

        if initial_address == address:
            color = '#FF0000'

        if address in SUSPICIUS_ADDRESSES:
            color = '#FF00FF'

        net.add_node(address, label=label, title=address,
                     value=balance, color=color)

    for i, (_, tx) in enumerate(tqdm(txs.items(), desc="Adding edges", unit="transaction")):
        try:
            net.add_edge(
                tx.address_from,
                tx.address_to,
                value=tx.value,
                color='green',
                title=tx.value
            )
        except AssertionError as e:
            logging.warning(f'Edge {i + 1}/{len(txs)} not added: {e}')

    return net


async def process_address(address, everspace_center_api: EverspaceCenterApi, tx_limit, new_addresses, full_transactions_data, processed_addresses):
    if address not in processed_addresses:
        raw_transactions = await everspace_center_api.get_transactions(
            address,
            tx_limit
        )

        if len(raw_transactions) < 5:
            SUSPICIUS_ADDRESSES.append(address)

        txs = process_raw_txs(raw_transactions)

        for tx in txs:
            new_addresses.add(tx.address_from)
            new_addresses.add(tx.address_to)
            if tx.id not in full_transactions_data:
                full_transactions_data[tx.id] = tx

        processed_addresses.append(address)


async def main():
    logging.basicConfig(level=logging.INFO)
    everspace_center_api = EverspaceCenterApi(EVERSPACE_CENTER_CONFIG)

    initial_address = '0:62a4c922bd869538396cb8994a67b0cfddf75b17860739fe88043349f1bc7c9c'
    addresses = [initial_address]
    processed_addresses = []
    full_transactions_data = {}

    tx_limit = TX_LIMIT

    for i in range(DEPTH):
        logging.info('Layer: ' + str(i + 1))
        new_addresses = set()

        tasks = []
        for address in tqdm(addresses):
            if i >= 1:
                tx_limit = 50
            task = asyncio.create_task(process_address(
                address, everspace_center_api, tx_limit, new_addresses, full_transactions_data, processed_addresses))
            tasks.append(task)

        await asyncio.gather(*tasks)

        addresses = set(new_addresses)
    logging.info('Visualizing..')
    net = await create_graph(full_transactions_data, addresses, everspace_center_api, initial_address)

    if not os.path.exists('./html'):
        os.makedirs('./html')
        
    directory = './html/'
    file_name = 'index.html'

    net.show(directory + file_name)
    logging.info('Ready.')

asyncio.run(main())
