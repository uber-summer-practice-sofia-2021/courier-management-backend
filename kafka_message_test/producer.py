from kafka import KafkaProducer
import json

KAFKA_TOPIC = "trips"
KAFKA_SERVERS = ["0.0.0.0:9092"]

producer = KafkaProducer(
    bootstrap_servers=KAFKA_SERVERS,
    value_serializer=lambda v: json.dumps(v).encode("utf-8"),
)

producer.send(KAFKA_TOPIC, {"test": "data"})
producer.flush()
