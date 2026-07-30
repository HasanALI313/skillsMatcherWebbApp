from kafka import KafkaConsumer
import json

consumer = KafkaConsumer(
    "orders",
    bootstrap_servers="localhost:9092",
    group_id="consumerOne",
    auto_offset_reset="latest",
    consumer_timeout_ms=90000,  # 90 seconds
    value_deserializer=lambda x: json.loads(x.decode("utf-8"))
)

print("Waiting for orders...")

for message in consumer:
    print(message.value)

print("No messages received for 90 seconds. Exiting.")