from kafka import KafkaProducer
from flask import json

class Producer:
    def __init__(self):
        pass

    def produce(self, topic, data):
        
        KAFKA_SERVERS = ["kafka:9092", "0.0.0.0:9092"]

        producer = KafkaProducer(
            bootstrap_servers=','.join(KAFKA_SERVERS),
            value_serializer=lambda v: json.dumps(v).encode("utf-8")
        )

        # send message to kafka
        producer.send(topic, data)
        producer.flush()

def message_kafka(topic, data):
    Producer().produce(topic, data)