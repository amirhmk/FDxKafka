import sys
import configparser
import json
import os
import time
from datetime import datetime, timedelta
from kafka import KafkaProducer
import numpy as np


sasl_mechanism = 'PLAIN'
security_protocol = 'SASL_PLAINTEXT'

DEFAULT_TIMEOUT=5000
SLEEP_TIME = int(os.environ.get("SLEEP_TIME", 300))

# Kafka producer
KAFKA_BROKER_URL = (
    os.environ.get("KAFKA_BROKER_URL")
    if os.environ.get("KAFKA_BROKER_URL")
    else "localhost:9092"
)
TOPIC_NAME = (
    os.environ.get("TOPIC_NAME") if os.environ.get("TOPIC_NAME") else "test"
)

KAFKA_USERNAME = (
    os.environ.get("KAFKA_USERNAME") if os.environ.get("KAFKA_USERNAME") else ""
)
KAFKA_PASSWORD = (
    os.environ.get("KAFKA_PASSWORD") if os.environ.get("KAFKA_PASSWORD") else ""
)


class producer:

    def __init__(self):
        
        self.producer = KafkaProducer(bootstrap_servers = KAFKA_BROKER_URL,
                         sasl_plain_username = KAFKA_USERNAME,
                         sasl_plain_password = KAFKA_PASSWORD,
                         security_protocol = security_protocol,
                         sasl_mechanism = sasl_mechanism,
                         value_serializer=lambda x: x.encode("utf8"),
                         api_version=(0, 11, 5),
                         max_request_size=104857600,
                         retries=5,
                         max_block_ms=DEFAULT_TIMEOUT)

    def run(self):
        date_to = datetime.utcnow()
        msg = "hello world"
        print(f'Sending kafka msg to {TOPIC_NAME}')
        while(True):
            try:
                self.producer.send(TOPIC_NAME, value=msg)
                self.producer.flush()
                print('Done')
            except:
                print("Unexpected error:", sys.exc_info())
            time.sleep(5)

if __name__ == "__main__":
    print(f"Starting producer for broker at {KAFKA_BROKER_URL}")
    service = producer()
    service.run()
    # time.sleep(10) #adding sleep here just to be able to see the logs after running.
