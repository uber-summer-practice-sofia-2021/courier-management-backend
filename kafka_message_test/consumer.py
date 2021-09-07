from kafka import KafkaConsumer
import json

KAFKA_TOPIC = "trips"

consumer = KafkaConsumer(
    KAFKA_TOPIC,
    bootstrap_servers="0.0.0.0:9092",
    value_deserializer=lambda v: json.loads(v.decode("utf-8")),
)
for message in consumer:
    print(message.value)
