from kafka import KafkaConsumer
import json, os

consumer = KafkaConsumer(
    "trips",
    bootstrap_servers=os.environ['KAFKA_BROKERS'].split(','),
    value_deserializer=lambda v: json.loads(v.decode("utf-8")),
    auto_offset_reset="earliest",
    enable_auto_commit=True,
)

for message in consumer:
    print(message.value)
