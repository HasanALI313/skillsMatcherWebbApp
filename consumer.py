from kafka import KafkaConsumer
import json

consumer = KafkaConsumer(
    "skills_matches",
    "job_searches",
    "cv_generations",
    bootstrap_servers="localhost:9092",
    group_id="app_analytics",
    auto_offset_reset="latest",
    value_deserializer=lambda x: json.loads(x.decode("utf-8")),
)

print("Listening for events on: skills_matches, job_searches, cv_generations")
print("Press Ctrl+C to stop.\n")

for message in consumer:
    print(f"[{message.topic}] {message.value}")
