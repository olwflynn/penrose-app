from flask import Flask, request, jsonify
import json
from kafka import KafkaConsumer, KafkaProducer

def create_app():

    app = Flask(__name__)
    app.config.from_pyfile('settings.py')
    producer = KafkaProducer(
        bootstrap_servers = app.config.get('KAFKA_SERVER'),
        api_version = (0, 11, 15)
    )

    @app.route("/")
    def getTest():
        return "It works we got it!!"

    @app.route("/kafka/pushTransaction", methods=["POST"])
    def kafkaProducer():
        req = request.get_json()
        json_payload = json.dumps(req)
        json_payload = str.encode(json_payload)
        print("trying to send to kafka")
        producer.send(app.config.get('TOPIC_NAME'), json_payload)
        producer.flush()
        print("Sent to kafka")
        return jsonify({"message": "You sent a cool message to kafka", "status": "pass"})

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True, port = 5000)


##TODO rm -r /tmp/zookeeper1 and /tmp/zookeeper once have taken kafka down
##TODO create docker image of the flask app for docker

##TODO figure out if we actually need endpoint to post events to. What else do we need endpoints e.g. choose contracts