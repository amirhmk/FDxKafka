import sys
import configparser
import json
import os
import time
from datetime import datetime, timedelta
from kafka import KafkaProducer
import numpy as np
import ssl


sasl_mechanism = 'PLAIN'
security_protocol = 'SASL_SSL'

# Create a new context using system defaults, disable all but TLS1.2
context = ssl.create_default_context()
context.options &= ssl.OP_NO_TLSv1
context.options &= ssl.OP_NO_TLSv1_1

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
                         ssl_context = context,
                         sasl_mechanism = sasl_mechanism,
                         api_version = (0,10),
                         retries=5,
                         max_block_ms=DEFAULT_TIMEOUT)
        # KafkaProducer(
        #     bootstrap_servers=KAFKA_BROKER_URL,
        #     value_serializer=lambda x: x.encode("utf8"),
        #     api_version=(0, 11, 5),
        # )

    def run(self):
        date_to = datetime.utcnow()
        msg = f"'date': '{date_to}'"
        print('Sending kafka msg')
        try:
            self.producer.send(TOPIC_NAME, value=msg)
            self.producer.flush()
            print('Done')
        except:
            print("Unexpected error:", sys.exc_info()[0])
            raise

if __name__ == "__main__":
    print(f"Starting producer for broker at {KAFKA_BROKER_URL}")
    service = producer()
    service.run()
    time.sleep(10) #adding sleep here just to be able to see the logs after running.
