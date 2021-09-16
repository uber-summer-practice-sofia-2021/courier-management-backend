import os
from kafka import KafkaProducer
from flask import json, current_app
import os


class Producer:
    def __init__(self):
        pass

    def produce(self, topic, data):

        producer = KafkaProducer(
            bootstrap_servers=os.environ['KAFKA_BROKERS'].split(','),
            value_serializer=lambda v: json.dumps(v).encode("utf-8"),
        )

        # send message to kafka
        ack = producer.send(topic, value=data)
        metadata = ack.get()
        current_app.logger.debug(metadata.topic)
        current_app.logger.debug(metadata.partition)
