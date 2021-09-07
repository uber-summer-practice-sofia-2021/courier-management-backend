from kafka import KafkaProducer
from flask import jsonify

class Producer:
    def __init__(self):
        pass

    def produce(self, topic, data):
        
        KAFKA_TOPIC = "trips"
        KAFKA_SERVERS = ["0.0.0.0:9092"]

        producer = KafkaProducer(
            bootstrap_servers=','.join(KAFKA_SERVERS),
            value_serializer=lambda v: lambda v: jsonify(v)
        )

        # send message to kafka
        producer.send(KAFKA_TOPIC, data)
        producer.flush()
        producer.close()
