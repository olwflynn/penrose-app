# import the following dependencies
from kafka import KafkaConsumer, KafkaProducer
import requests
from web3 import Web3
import asyncio
import os, yaml, json

def web3_setup(contracts_yaml_):
    # add your blockchain connection information
    infura_url = 'http://127.0.0.1:8545/'
    web3 = Web3(Web3.HTTPProvider(infura_url))

    #TODO also need to add and pull out the topics from the config
    # there is only one item = 'contracts' and doc = the dicts of contract addresses and abis
    # create array of web3 contracts
    web3_contracts = []
    for item, doc in contracts_yaml_.items():
        for address, abi_dict in doc.items():
            abi = json.loads(abi_dict['abi'])
            contract = web3.eth.contract(address=address, abi=abi)
            web3_contracts.append(contract)

    return web3_contracts


# define function to handle events and print to the console
def handle_event(event, producer_, topic_):
    event_json = Web3.toJSON(event)
    print(event_json)
    # response = requests.post('http://localhost:5000/kafka/pushTransaction',json=event_json)
    event_json = str.encode(event_json)
    producer_.send(topic_, event_json)
    producer_.flush()
    print("Sent message to kafka")



# asynchronous defined function to loop
# this loop sets up an event filter and is looking for new entires for the "PairCreated" event
# this loop runs on a poll interval
async def log_loop(contracts, poll_interval, producer_, topic_):
    filters = create_filters(contracts)
    while True:
        for event_filter in filters:
            for StorageEvent in event_filter.get_new_entries():
                handle_event(StorageEvent, producer_, topic_)
            await asyncio.sleep(poll_interval)

def create_filters(contracts):
    event_filter_array = []
    for web3_contract in contracts:
        event_filter = web3_contract.events.StorageEvent.createFilter(fromBlock='latest')
        event_filter_array.append(event_filter)
    return event_filter_array

def get_or_create_eventloop():
    try:
        return asyncio.get_event_loop()
    except RuntimeError as ex:
        if "There is no current event loop in thread" in str(ex):
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            return asyncio.get_event_loop()

# when main is called
# create a filter for the latest block and look for the "PairCreated" event for the uniswap factory contract
# run an async loop
# try to run the log_loop function above every 2 seconds
def connect_subscriptions(producer, topic, contracts_yaml):
    web3_contracts = web3_setup(contracts_yaml)
    loop = get_or_create_eventloop()
    print("starting the loop")
    try:
        loop.run_until_complete(
            asyncio.gather(
                log_loop(web3_contracts, 2, producer, topic)))
    finally:
        # close loop to free up system resources
        loop.close()


# if __name__ == "__main__":
#     connect_subscriptions()