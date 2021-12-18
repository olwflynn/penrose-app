from flask import Flask, request, jsonify, render_template, make_response
import json, yaml, os
from kafka import KafkaConsumer, KafkaProducer
from .subscribe import connect_subscriptions

def create_app():

    app = Flask(__name__, template_folder="templates")
    app.config.from_pyfile('settings.py')
    basedir = os.path.abspath(os.path.dirname(__file__))

    with open(os.path.join(basedir, 'contracts.yml'), 'r') as stream:
        contracts_yaml = yaml.safe_load(stream)

    producer = KafkaProducer(
        bootstrap_servers = app.config.get('KAFKA_SERVER'),
        api_version = (0, 11, 15)
    )

    topic = app.config.get('TOPIC_NAME')

    @app.route("/")
    def home():
        return render_template("index.html",
                               title="Admin Panel",
                               header="This is where you can connect to contracts!",
                               all_contracts=contracts_yaml)

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
        contract_address = "nada"
        if request.method == "POST":
            contract_address = request.form.get('contract_address')
        return make_response(
            contract_address,
            200,
        )

    @app.route("/api/v1/subscribe", methods=["GET"])
    def subscribe():
        return connect_subscriptions(producer, topic, contracts_yaml)

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True, port = 5000)


##TODO create docker image of the flask app for docker
##TODO figure out if we actually need endpoint to post events to. What else do we need endpoints e.g. choose contracts
##TODO create Admin UI to add and store contracts and abis for which to subscribe to and configure which topics to write to
##TODO do something crypto specific value add with the events; enable to switch between blockchains by config and add event names
##TODO push kafka events to db or analytics
##TODO make the base template nicer and extend the others
##TODO create cancel and update subscription endpoint