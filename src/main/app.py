from flask import Flask, request, jsonify, render_template, redirect, url_for
import json, yaml, os
from kafka import KafkaProducer
from .subscribe import run
import logging
from web3 import Web3

def create_app():

    app = Flask(__name__, template_folder="templates")
    app.config.from_pyfile('settings.py')
    basedir = os.path.abspath(os.path.dirname(__file__))

    #local or public blockchain. Set to false if developing locally
    public_blockchain = True

    def load_yaml():
        with open(os.path.join(basedir, 'contracts.yml'), 'r') as stream:
            contracts_yaml = yaml.safe_load(stream)
            return contracts_yaml

    def write_yaml(updated_yaml):
        with open(os.path.join(basedir, 'contracts.yml'),'w') as yamlfile:
            yaml.safe_dump(updated_yaml, yamlfile)

    def get_contract_event_types(_yaml):
        contract_event_types = {}
        for contract_address in _yaml['contracts']:
            contract_yaml = _yaml['contracts'][contract_address]
            contract_abi = json.loads(contract_yaml['abi'])
            contract_event_types[contract_address] = []
            for obj in contract_abi:
                try:
                    if obj['type'] == 'event':
                        contract_event_types[contract_address].append(obj['name'])
                except KeyError:
                    pass
        return contract_event_types

    contracts_yaml = load_yaml()
    contract_event_types = get_contract_event_types(contracts_yaml)
    print(contract_event_types)

    producer = KafkaProducer(
        bootstrap_servers = app.config.get('KAFKA_SERVER'),
        api_version = (0, 11, 15)
    )

    # This should ultimately be taken from the contracts config file not be an env variable
    topic = app.config.get('TOPIC_NAME')
    print(topic)
    infura_url = app.config.get('PUBLIC_INFURA_URL')
    print(infura_url)

    subscription_threads_dict = {}

    @app.before_first_request
    def all_contracts_inactive():
        for contract_address in contracts_yaml['contracts']:
            contract_yaml = contracts_yaml['contracts'][contract_address]
            contract_yaml['active'] = False
        write_yaml(contracts_yaml)
        print('Set all contract subscriptions to inactive')

    @app.route("/")
    def home():
        contracts_yaml = load_yaml()
        emptyBanner = ''
        return render_template("index.html",
                               title="Admin Panel",
                               header="This is where you can connect to contracts!",
                               contracts_yaml=contracts_yaml,
                               kowl_server=app.config.get('KOWL_SERVER'),
                               banner=emptyBanner,
                               contract_event_types=contract_event_types)

    @app.route("/kafka/pushTransaction", methods=["POST"])
    def kafkaProducer():
        req = request.get_json()
        json_payload = json.dumps(req)
        json_payload = str.encode(json_payload)
        print("trying to send to kafka")
        producer.send(topic, json_payload)
        producer.flush()
        print("Sent to kafka")
        return jsonify({"message": "You sent a cool message to kafka", "status": "pass"})

    @app.route("/api/v1/contract", methods=["POST", "GET", "PUT", "DELETE"])
    def contract():
        headers = {"Content-Type": "application/json"}
        contracts_yaml = load_yaml()
        if request.method == "POST":
            req = request.form
            try:
                contract_address = req.get('contract_address')
                contract_address = Web3.toChecksumAddress(contract_address)
                contract_abi = req.get('contract_abi')
                contract_abi = json.loads(contract_abi)
                contract_abi = json.dumps(contract_abi)
                print(contract_abi)
                yaml_append_dict = {contract_address: {"abi": contract_abi, "web3provider": "ethereum mainnet",\
                                                       "active": False, "topic": None}}
                contracts_yaml['contracts'].update(yaml_append_dict)
                write_yaml(contracts_yaml)
                successBanner = 'You successfully added a new contract with address {}'.format(contract_address)
            except json.JSONDecodeError:
                return "Bad Request", 400
            except ValueError:
                return "Invalid Contract Address", 400

            return render_template("index.html",
                                   title="Admin Panel",
                                   header="This is where you can connect to contracts!",
                                   contracts_yaml=contracts_yaml,
                                   kowl_server=app.config.get('KOWL_SERVER'),
                                   banner=successBanner,
                                   contract_event_types=contract_event_types)
        return redirect(url_for('/'))

    @app.route("/api/v1/contract/<contract_address>/subscribe", methods=["POST"])
    def toggle_subscription(contract_address):
        contracts_yaml = load_yaml()
        req = request.form
        subscription_action = req.get('toggle_subscription')

        if public_blockchain:
            infura_url = app.config.get('PUBLIC_INFURA_URL')
        else:
            infura_url = app.config.get('LOCAL_INFURA_URL')
        print('URLLLLLL', infura_url)
        if subscription_action == "Subscribe":
            contract_event_type = req.get('contract_event_type')
            subscription_thread = run(producer, topic, contracts_yaml, contract_address, contract_event_type, infura_url)
            subscription_threads_dict[contract_address] = subscription_thread
            print(subscription_threads_dict)
            ## update the config with active == true
            contract_yaml = contracts_yaml['contracts'][contract_address]
            contract_yaml['active'] = True
            write_yaml(contracts_yaml)
            successBanner = 'You successfully subscribed contract {}'.format(contract_address)
            logging.info('Main: Successfully subscribed a contract')

        else:
            ## stop subscription_thread and update config with active == false
            print('stopping subscription_thread')
            subscription_thread = subscription_threads_dict[contract_address]
            subscription_thread.stop_thread()
            print('thread stopped')
            subscription_thread.join()
            print('thread joined')
            contract_yaml = contracts_yaml['contracts'][contract_address]
            contract_yaml['active'] = False
            write_yaml(contracts_yaml)
            successBanner = 'You successfully unsubscribed from contract {}'.format(contract_address)

        return render_template("index.html",
                               title="Admin Panel",
                               header="This is where you can connect to contracts!",
                               contracts_yaml=contracts_yaml,
                               kowl_server=app.config.get('KOWL_SERVER'),
                               banner=successBanner,
                               contract_event_types=contract_event_types)

    return app

app = create_app()

if __name__ == "__main__":
    format = "%(asctime)s: %(message)s"
    logging.basicConfig(format=format, level=logging.INFO,
                        datefmt="%H:%M:%S")
    with app.app_context():
        app.run(debug=True, port = 5000)

##TODO USER JOURNEY MVP (DONE):
## start subscribing to the new contract. This starts subscribing and changes the state in the UI to active for a single contract type
## stop subscribing to the contract. This stops subscribing and changes the state back to not subscribed in the UI
## send transaction to ropsten contract so that it emits event e.g. via etherscan and be subscribed to it in the app


##TODO MVP
## create docker image of the flask app for docker which also creates blockchain development
## Write tests (contract create, change status to active, subscribe to contract and send event to kafka)
## Clean up unneeded code; refactor connect_subscriptions
## Add feature to show subscribe at event level in the UI and yaml file
## try using the truffle app to interact with events or try to read something from the contract in order to make sure we
## connected.

##TODO BUGS:
## figure out why logging is not working
## keeping the state of the running threads is very brittle as in a dict atm
## enable the error handling to be passed from child subscribe thread to parent app thread so it can be handled
## add error handling for when can't connect to blockchain or kafka
## add error handling for when cant connect to a particular contract
## not picking up event types of some abis

##TODO NEW FEATURES:
## show kafka status and be able to create topic from the UI
## make the base template nicer and extend the others
## push kafka events to db or analytics
## enable to switch between blockchains
## get abi automatically from address instead of having to paste in as sometimes not available on etherscan



## TODO LAUNCH ON ROPSTEN:
## change config to enable infura_url from ropsten network
## input address and abi of contract on ropsten and choose the relevant contract


## TODO USE CASE NFT NOTIFICATIONS:
## Subscribe to ERC721 events at a particular contract e.g. BAYC https://github.com/OpenZeppelin/openzeppelin-contracts/tree/master/contracts/token/ERC721
## Alert when it sends a change owner event on discord