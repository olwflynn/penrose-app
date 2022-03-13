# import the following dependencies
import threading
from kafka import KafkaConsumer, KafkaProducer
from web3 import Web3
import asyncio
import os, yaml, json, time
import logging
from .discord_client import send_message_to_discord

def web3_setup(contracts_yaml_, infura_url_):
    # add your blockchain connection information
    infura_url = infura_url_
    web3 = Web3(Web3.HTTPProvider(infura_url))
    print(web3, 'we have successfully connected to blockchain')
    print(web3.provider)
    web3_contracts = []
    for item, doc in contracts_yaml_.items():
        for address, abi_dict in doc.items():
            try:
                abi = json.loads(abi_dict['abi'])
            except KeyError:
                print('Contract at address {} has no abi stored. Will assume NFT events are present and add Transfer event as abi'.format(address))
                abi = json.loads('[{"anonymous": false, "inputs": [{"indexed": false, "internalType": "address","name": "user", "type": "address"}, \
                {"indexed": false, "internalType": "uint256","name": "amount", "type": "uint256"}], "name": "Transfer", "type": "event"}]')
            contract = web3.eth.contract(address=Web3.toChecksumAddress(address), abi=abi)
            print('Ready to subscribe to {} contract'.format(address))
            web3_contracts.append(contract)

    return web3_contracts

def get_web3_contract_by_address(list_of_web3_contracts, contract_address):
    for contract in list_of_web3_contracts:
        if contract.address == Web3.toChecksumAddress(contract_address):
            web3_contract = contract
            return web3_contract
    return 'Contract address is not in list of contracts'
# define function to handle events and print to the console
def handle_event(event, producer_, topic_):
    event_json = Web3.toJSON(event)
    print(event_json)
    # response = requests.post('http://localhost:5000/kafka/pushTransaction',json=event_json)
    event_str = str.encode(event_json)
    producer_.send(topic_, event_str)
    producer_.flush()
    send_message_to_discord(url=os.environ.get('DISCORD_WEBHOOK_URL'), message=event_json, parse=True)
    print("Sent message to kafka")



# asynchronous defined function to loop
# this loop sets up an event filter and is looking for new entires for the "PairCreated" event
# this loop runs on a poll interval


def create_filter(web3_contract, eventType):
    eventObj = web3_contract.events[eventType]
    print('WE ARE HERE -------')
    try:
        event_filter = eventObj.createFilter(fromBlock='latest')
        return event_filter
    except ConnectionError as e:
        return 'Connection to blockchain refused while trying to subscribe to contract - pls check connection'

def get_or_create_eventloop():
    try:
        return asyncio.get_event_loop()
    except RuntimeError as ex:
        if "There is no current event loop in thread" in str(ex):
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            return asyncio.get_event_loop()

class SubscriptionThread(threading.Thread):
    def __init__(self, contract_address, web3_contracts, producer, topic, contract_event_type):
        threading.Thread.__init__(self)
        self.contract_address = contract_address
        self.web3_contracts = web3_contracts
        self.producer = producer
        self.topic = topic
        self.contract_event_type = contract_event_type
        self._running = True

    def run(self):
        self.exc = None
        # try:
        print('running ', self.contract_address, 'thread')
        web3_contract = get_web3_contract_by_address(self.web3_contracts, self.contract_address)
        print(web3_contract, self.contract_event_type)

        filter = create_filter(web3_contract, self.contract_event_type)
        while self._running:

            for event in filter.get_new_entries():
                handle_event(event, self.producer, self.topic)
            # await asyncio.sleep(poll_interval)
            time.sleep(2)
        # except BaseException as e:
        #     self.exc = e
        #     print('THIS IS EXCEPTION IN THE SUBSCRIBE THREAD', e)
            # threading.Thread.join(self)
        # finally:
        #     print(self.contract_address, 'thread ended')
        #     threading.Thread.join(self)
        #     if self.exc:
        #             raise self.exc
        #     print('thread JOINED AND ENDED AND EXCEPTION MAY BE RAISED')

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

    def join(self):
        threading.Thread.join(self)
        if self.exc:
            raise self.exc

def connect_subscriptions(producer, topic, contracts_yaml, contract_address, contract_event_type, infura_url):
    web3_contracts = web3_setup(contracts_yaml, infura_url)
    in_scope_web3_contracts = [contract for contract in web3_contracts if contract.address == Web3.toChecksumAddress(contract_address)]
    print([contract.address for contract in in_scope_web3_contracts][0], 'this is the contract we are subscribing to')
    # loop = get_or_create_eventloop()
    # print("starting the loop")

    subscription_thread = SubscriptionThread(contract_address=contract_address, web3_contracts=web3_contracts, \
                                             producer=producer, topic=topic, contract_event_type=contract_event_type)
    print("starting thread for ", subscription_thread.contract_address)
    logging.info("Thread:  starting thread")
    subscription_thread.start()
    print("Thread:  started thread XXXXXXX")

    # try:
    #     subscription_thread.join()
    # except Exception as e:
    #     print("Exception Handled in SUBSCRIBE BUT MAIN, Details of the Exception:", e)

    return subscription_thread

def run(producer, topic, contracts_yaml, contract_address, contract_event_type, infura_url):
    return connect_subscriptions(producer, topic, contracts_yaml, contract_address, contract_event_type, infura_url)


# if __name__ == "__main__":
#     connect_subscriptions()