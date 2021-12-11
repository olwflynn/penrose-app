import self as self

from src.main.app import KafkaProducer
#
# def test_producer():
#     """
#     GIVEN the producer
#     WHEN API call is made
#     THEN check the same message in the body of the API call is what is in kafka
#     """
#     flask_app = app.run(debug=True, port = 5000)
#     KafkaProducer("http://127.0.0.1:5000/kafka/pushTransaction","test json load")
