from kafka import KafkaProducer
import json
import time
import random

producer = KafkaProducer(
    bootstrap_servers="localhost:9092",  # Tell the producer where Kafka is running
    value_serializer=lambda v: json.dumps(v).encode("utf-8")  # Serialize Python objects to JSON bytes
)

# Sample products
products = [
    "Laptop",
    "Phone",
    "Keyboard",
    "Monitor",
    "Mouse"
]

# Send exactly 10 orders
for i in range(10):

    order = {
        "order_id": random.randint(1000, 9999),
        "product": random.choice(products),
        "quantity": random.randint(1, 5)
    }

    producer.send("orders", order)

    print(f"Message {i + 1}/10 sent: {order}")

    time.sleep(2)

# Ensure all messages are sent before exiting
producer.flush()

print("\nAll 10 messages have been sent.")