
import os, sys
from kafka import KafkaConsumer, KafkaProducer
import datetime as dt
# import ast

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

if __name__ == "__main__":
    
    print(f"{str(dt.datetime.now())} Setting up Kafka consumer at {KAFKA_BROKER_URL}")
    consumer = KafkaConsumer(TOPIC_NAME, bootstrap_servers=KAFKA_BROKER_URL,
                            sasl_plain_username = KAFKA_USERNAME,
                            sasl_plain_password = KAFKA_PASSWORD,
                            security_protocol = security_protocol,
                            sasl_mechanism = sasl_mechanism)

    # producer = KafkaProducer(bootstrap_servers = KAFKA_BROKER_URL,
    #                      sasl_plain_username = KAFKA_USERNAME,
    #                      sasl_plain_password = KAFKA_PASSWORD,
    #                      security_protocol = security_protocol,
    #                      sasl_mechanism = sasl_mechanism,
    #                     #  value_serializer=lambda x: x.encode("utf8"),
    #                      api_version=(0, 11, 5),
    #                      max_request_size=104857600,
    #                      retries=5,
    #                      max_block_ms=DEFAULT_TIMEOUT)
    print('Waiting for msg...')
    for msg in consumer:
        # print('got one!')
        msg = msg.value.decode('utf-8')
        print(f"{str(dt.datetime.now())} Message received : {msg}")

        # data = ast.literal_eval(msg)
        
        # print("Sending it to Sink")
        # dic = json.dumps(dic)
        # producer.send(SINK_TOPIC, value = dic)
        # print("Sent")

    print("Bye-Bye")