from kafka import KafkaConsumer
import json

consumer = KafkaConsumer(
    "orders",
    bootstrap_servers="localhost:9092",
    group_id="consumerTwo",
    auto_offset_reset="latest", ### each kafka messsage has an offset and that's how it knows what's been read.
    consumer_timeout_ms=20000,  # 20 seconds
    value_deserializer=lambda x: json.loads(x.decode("utf-8"))
)

print("Waiting for orders...")

for message in consumer:
    print(message.value)

print("No messages received for 20 seconds. Exiting.")