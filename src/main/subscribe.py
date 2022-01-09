# import the following dependencies
import threading
from kafka import KafkaConsumer, KafkaProducer
from web3 import Web3
import asyncio
import os, yaml, json, time
import logging
import ctypes

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
def log_loop(contracts, poll_interval, producer_, topic_):
    filters = create_filters(contracts)
    logging.info("Thread:  before loop and filters are %s", filters)
    print("Thread:  before loop and filters are %s", filters)
    # while True:
    #     logging.info("Thread:  in loop now...")
    #     for event_filter in filters:
    #         for StorageEvent in event_filter.get_new_entries():
    #             handle_event(StorageEvent, producer_, topic_)
    #         # await asyncio.sleep(poll_interval)
    #         time.sleep(poll_interval)
    return filters

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

class SubscriptionThread(threading.Thread):
    def __init__(self, contract_address, web3_contracts, producer, topic):
        threading.Thread.__init__(self)
        self.contract_address = contract_address
        self.web3_contracts = web3_contracts
        self.producer = producer
        self.topic = topic
        self._running = True

    def run(self):

        try:
            print('running ', self.contract_address, 'thread')
            filters = log_loop(self.web3_contracts, 2, self.producer, self.topic)
            while self._running:
                for event_filter in filters:
                    for StorageEvent in event_filter.get_new_entries():
                        handle_event(StorageEvent, self.producer, self.topic)
                    # await asyncio.sleep(poll_interval)
                    time.sleep(2)

        finally:
            print(self.contract_address, 'thread ended')

    def get_id(self):

        # returns id of the respective thread
        if hasattr(self, '_thread_id'):
            return self._thread_id
        for id, thread in threading._active.items():
            if thread is self:
                return id

    def stop_thread(self):
        # thread_id = self.get_id()
        # res = ctypes.pythonapi.PyThreadState_SetAsyncExc(thread_id,
        #                                                  ctypes.py_object(SystemExit))
        # if res > 1:
        #     ctypes.pythonapi.PyThreadState_SetAsyncExc(thread_id, 0)
        #     print('Exception raise failure')
        # print('stopping thread')
        self._running = False


def connect_subscriptions(producer, topic, contracts_yaml, contract_address):
    web3_contracts = web3_setup(contracts_yaml)
    in_scope_web3_contracts = [contract for contract in web3_contracts if contract.address == contract_address]
    print([contract.address for contract in in_scope_web3_contracts], 'these are the contracts we are subscribing to')
    # loop = get_or_create_eventloop()
    # print("starting the loop")

    subscription_thread = SubscriptionThread(contract_address=contract_address, web3_contracts=web3_contracts, \
                                             producer=producer, topic=topic)
    print("starting thread for ", subscription_thread.contract_address)
    logging.info("Thread:  starting thread")
    subscription_thread.start()
    logging.info("Thread:  started thread")
    return subscription_thread
        # global stop_threads
        # if stop_threads:
        #     break
    # try:
    #     loop.run_until_complete(
    #         asyncio.gather(
    #             log_loop(web3_contracts, 2, producer, topic)))
    # finally:
    #     # close loop to free up system resources
    #     loop.close()
    # task = loop.create_task(log_loop(in_scope_web3_contracts, 2, producer, topic))
    # await task

def run(producer, topic, contracts_yaml, contract_address):
    return connect_subscriptions(producer, topic, contracts_yaml, contract_address)


# if __name__ == "__main__":
#     connect_subscriptions()