# import the following dependencies
import json

import requests
from web3 import Web3
import asyncio
import os, yaml

# add your blockchain connection information
infura_url = 'http://127.0.0.1:8545/'
web3 = Web3(Web3.HTTPProvider(infura_url))

basedir = os.path.abspath(os.path.dirname(__file__))

with open(os.path.join(basedir, 'contracts.yml'), 'r') as stream:
    contracts_yaml = yaml.safe_load(stream)


# there is only one item = 'contracts' and doc = the dicts of contract addresses and abis
# create array of web3 contracts
web3_contracts = []
for item, doc in contracts_yaml.items():
    for address, abi_dict in doc.items():
        abi = json.loads(abi_dict['abi'])
        contract = web3.eth.contract(address=address, abi=abi)
        web3_contracts.append(contract)

print(web3_contracts)

# define function to handle events and print to the console
def handle_event(event):
    event_json = Web3.toJSON(event)
    print(event_json)
    response = requests.post('http://localhost:5000/kafka/pushTransaction',json=event_json)
    return response


# asynchronous defined function to loop
# this loop sets up an event filter and is looking for new entires for the "PairCreated" event
# this loop runs on a poll interval
async def log_loop(contracts, poll_interval):
    filters = create_filters(contracts)
    while True:
        for event_filter in filters:
            for StorageEvent in event_filter.get_new_entries():
                handle_event(StorageEvent)
            await asyncio.sleep(poll_interval)

def create_filters(contracts):
    event_filter_array = []
    for web3_contract in contracts:
        event_filter = web3_contract.events.StorageEvent.createFilter(fromBlock='latest')
        event_filter_array.append(event_filter)
    return event_filter_array

# when main is called
# create a filter for the latest block and look for the "PairCreated" event for the uniswap factory contract
# run an async loop
# try to run the log_loop function above every 2 seconds
def main():

    #block_filter = web3.eth.filter('latest')
    # tx_filter = web3.eth.filter('pending')
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(
            asyncio.gather(
                log_loop(web3_contracts, 2)))
        # log_loop(block_filter, 2),
        # log_loop(tx_filter, 2)))
    finally:
        # close loop to free up system resources
        loop.close()


if __name__ == "__main__":
    main()