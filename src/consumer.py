from kafka import KafkaConsumer
import json

KAFKA_TOPIC = "trips"

consumer = KafkaConsumer(
    KAFKA_TOPIC,
    bootstrap_servers=["localhost:9092", "kafka:9092"],
    value_deserializer=lambda v: json.loads(v.decode("utf-8")),
    auto_offset_reset="earliest",
    enable_auto_commit=True,
)

for message in consumer:
    print(message.value)
