from flask import Flask, request, jsonify
import json
from kafka import KafkaConsumer, KafkaProducer



app = Flask(__name__)

TOPIC_NAME = "TRANSACTIONS"
KAFKA_SERVER = "localhost:9092"

producer = KafkaProducer(
    bootstrap_servers = KAFKA_SERVER,
    api_version = (0, 11, 15)
)


@app.route("/kafka/pushTransaction", methods=["POST"])
def kafkaProducer():
    req = request.get_json()
    json_payload = json.dumps(req)
    json_payload = str.encode(json_payload)
    print("trying to send to kafka")
    producer.send(TOPIC_NAME, json_payload)
    producer.flush()
    print("Sent to kafka")

    return jsonify({"message": "You sent a cool message to kafka", "status": "pass"})


if __name__ == "__main__":
    app.run(debug=True, port = 5000)

##TODO create a truffle smart contract to test with. probs in the test folder

##TODO rm -r /tmp/zookeeper1 and /tmp/zookeeper once have taken kafka down
##TODO figure out how to store environment variables in flask app
##TODO create docker image of the flask app for docker

##TODO figure out why it does not seem like we are actually writing to the docker kafka even though it is succeeding