# import the following dependencies
import json

import requests
from web3 import Web3
import asyncio

# add your blockchain connection information
infura_url = 'http://127.0.0.1:8545/'
web3 = Web3(Web3.HTTPProvider(infura_url))

simple_storage_address = '0x6325e6e555929727742243c2595034227c828E46'
simple_storage_abi = json.loads("""[
    {
        "anonymous": false,
        "inputs": [
            {
                "indexed": false,
                "internalType": "address",
                "name": "user",
                "type": "address"
            },
            {
                "indexed": false,
                "internalType": "uint256",
                "name": "amount",
                "type": "uint256"
            }
        ],
        "name": "StorageEvent",
        "type": "event"
    },
    {
        "constant": false,
        "inputs": [
            {
                "internalType": "uint256",
                "name": "x",
                "type": "uint256"
            }
        ],
        "name": "set",
        "outputs": [],
        "payable": false,
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "constant": true,
        "inputs": [],
        "name": "get",
        "outputs": [
            {
                "internalType": "uint256",
                "name": "",
                "type": "uint256"
            }
        ],
        "payable": false,
        "stateMutability": "view",
        "type": "function"
    }
]""")

contract = web3.eth.contract(address=simple_storage_address, abi=simple_storage_abi)

# define function to handle events and print to the console
def handle_event(event):
    event_json = Web3.toJSON(event)
    print(event_json)
    response = requests.post('http://localhost:5000/kafka/pushTransaction',json=event_json)
    return response


# asynchronous defined function to loop
# this loop sets up an event filter and is looking for new entires for the "PairCreated" event
# this loop runs on a poll interval
async def log_loop(event_filter, poll_interval):
    while True:
        for StorageEvent in event_filter.get_new_entries():
            handle_event(StorageEvent)
        await asyncio.sleep(poll_interval)

# when main is called
# create a filter for the latest block and look for the "PairCreated" event for the uniswap factory contract
# run an async loop
# try to run the log_loop function above every 2 seconds
def main():
    event_filter = contract.events.StorageEvent.createFilter(fromBlock='latest')
    #block_filter = web3.eth.filter('latest')
    # tx_filter = web3.eth.filter('pending')
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(
            asyncio.gather(
                log_loop(event_filter, 2)))
        # log_loop(block_filter, 2),
        # log_loop(tx_filter, 2)))
    finally:
        # close loop to free up system resources
        loop.close()


if __name__ == "__main__":
    main()