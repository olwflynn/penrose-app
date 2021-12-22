from flask import Flask, request, jsonify, render_template, make_response, redirect, url_for
import json, yaml, os
from kafka import KafkaConsumer, KafkaProducer
from .subscribe import connect_subscriptions, run

def create_app():

    app = Flask(__name__, template_folder="templates")
    app.config.from_pyfile('settings.py')
    basedir = os.path.abspath(os.path.dirname(__file__))

    def load_yaml():
        with open(os.path.join(basedir, 'contracts.yml'), 'r') as stream:
            contracts_yaml = yaml.safe_load(stream)
            return contracts_yaml

    def write_yaml(updated_yaml):
        with open(os.path.join(basedir, 'contracts.yml'),'w') as yamlfile:
            yaml.safe_dump(updated_yaml, yamlfile)

    contracts_yaml = load_yaml()

    producer = KafkaProducer(
        bootstrap_servers = app.config.get('KAFKA_SERVER'),
        api_version = (0, 11, 15)
    )

    # This should ultimately be taken from the contracts config file not be an env variable
    topic = app.config.get('TOPIC_NAME')

    @app.route("/")
    def home():
        contracts_yaml = load_yaml()
        emptyBanner = ''
        return render_template("index.html",
                               title="Admin Panel",
                               header="This is where you can connect to contracts!",
                               contracts_yaml=contracts_yaml,
                               kowl_server=app.config.get('KOWL_SERVER'),
                               banner=emptyBanner)

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
        contract_address = "nada"
        if request.method == "POST":
            req = request.form
            contract_address = req.get('contract_address')
            contract_abi = req.get('contract_abi')
            yaml_append_dict = {contract_address: {'abi':contract_abi, 'web3provider': 'ethereum mainnet',\
                                                   'active': False, 'topic': None}}
            print(type(contracts_yaml))
            print(yaml_append_dict)
            contracts_yaml['contracts'].update(yaml_append_dict)
            write_yaml(contracts_yaml)
            successBanner = 'You successfully added a new contract'

            return render_template("index.html",
                                   title="Admin Panel",
                                   header="This is where you can connect to contracts!",
                                   contracts_yaml=contracts_yaml,
                                   kowl_server=app.config.get('KOWL_SERVER'),
                                   banner=successBanner)
        return redirect(url_for('/'))

    @app.route("/api/v1/contract/<contract_address>/subscribe", methods=["GET"])
    def start_subscriptions(contract_address):
        contracts_yaml = load_yaml()
        # connect_subscriptions(producer, topic, contracts_yaml)
        run(producer, topic, contracts_yaml, contract_address)
        successBanner = 'You successfully subscribed a contract'
        return render_template("index.html",
                               title="Admin Panel",
                               header="This is where you can connect to contracts!",
                               contracts_yaml=contracts_yaml,
                               kowl_server=app.config.get('KOWL_SERVER'),
                               banner=successBanner)

    # @app.route("/api/v1/subscriptions/start", methods=["GET"])
    # def stop_subscriptions():

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True, port = 5000)


##TODO create docker image of the flask app for docker
##TODO subscribe API (DELETE, UPDATE, CREATE), provide subscriptions active, paused, cancelled state
##TODO do something crypto specific value add with the events; enable to switch between blockchains by config and add event names
##TODO push kafka events to db or analytics
##TODO add subscription whilst app is running to see what behaviour is like
##TODO ability to create different apps
##TODO make the base template nicer and extend the others
##TODO Write tests
##TODO figure out why we are double writing


##TODO USER JOURNEY:
## start subscribing to the new contract. This starts subscribing and changes the state in the UI to active
## stop subscribing to the contract. This stops subscribing and changes the state back to not subscribed in the UI