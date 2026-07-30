import json
import logging

_producer = None

logger = logging.getLogger(__name__)


def _get_producer():
    global _producer
    if _producer is None:
        try:
            from kafka import KafkaProducer
            _producer = KafkaProducer(
                bootstrap_servers="localhost:9092",
                value_serializer=lambda v: json.dumps(v).encode("utf-8"),
                max_block_ms=2000,
            )
        except Exception as e:
            logger.warning("Kafka not available: %s", e)
            _producer = False
    return _producer if _producer is not False else None


def send_event(topic, data):
    producer = _get_producer()
    if producer is None:
        return False
    try:
        producer.send(topic, data)
        producer.flush(timeout=1)
        return True
    except Exception as e:
        logger.warning("Kafka send failed: %s", e)
        return False


def send_skills_match(skills, matches):
    return send_event("skills_matches", {
        "skills": skills,
        "matches": [{"title": t, "score": s, "skills": sk} for t, s, sk in matches],
    })


def send_job_search(query, results_count):
    return send_event("job_searches", {
        "query": query,
        "results_count": results_count,
    })


def send_cv_generation(job_title, user_name):
    return send_event("cv_generations", {
        "job_title": job_title,
        "user_name": user_name,
    })
