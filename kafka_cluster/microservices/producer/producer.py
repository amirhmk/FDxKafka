import configparser
import json
import os
import time
from datetime import datetime, timedelta
from kafka import KafkaProducer
import numpy as np


SLEEP_TIME = int(os.environ.get("SLEEP_TIME", 300))

# Kafka producer
KAFKA_BROKER_URL = (
    os.environ.get("KAFKA_BROKER_URL")
    if os.environ.get("KAFKA_BROKER_URL")
    else "localhost:9092"
)
TOPIC_NAME = (
    os.environ.get("TOPIC_NAME") if os.environ.get("TOPIC_NAME") else "from_finnhub"
)


class producer:

    def __init__(self):
        
        self.producer = KafkaProducer(
            bootstrap_servers=KAFKA_BROKER_URL,
            value_serializer=lambda x: x.encode("utf8"),
            api_version=(0, 11, 5),
        )

    def run(self):
        date_from = self.last_poll_datetime
        date_to = datetime.utcnow()
        msg = f"{'date': '{date_to}'}"
        print(f'Sending kafka msg')
        self.producer.send(TOPIC_NAME, value=msg)
        self.producer.flush()
        


if __name__ == "__main__":
    print("Starting producer")
    service = producer()
    service.run()
    time.sleep(10) #adding sleep here just to be able to see the logs after running.
