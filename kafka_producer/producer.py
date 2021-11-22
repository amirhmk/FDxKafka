import sys
import os
import time
from datetime import datetime, timedelta
from kafka import KafkaProducer
import numpy as np

now = lambda : str(datetime.now())

KAFKA_MAX_SIZE = 104857600

class MsgSender:
    def __init__(self, server_address, options):
        self.init(server_address, options)
        self.producer = KafkaProducer(bootstrap_servers = self.KAFKA_BROKER_URL,
                         sasl_plain_username = self.KAFKA_USERNAME,
                         sasl_plain_password = self.KAFKA_PASSWORD,
                         security_protocol = self.security_protocol,
                         sasl_mechanism = self.sasl_mechanism,
                        #  value_serializer=lambda x: x.encode("utf8"),
                         value_serializer=lambda x: bytes(str(x), 'utf-8'),
                         api_version=(0, 11, 5),
                         max_request_size=self.MAX_SIZE,
                         retries=5,
                         max_block_ms=self.DEFAULT_TIMEOUT)


    def sendMsg(self, data : np.ndarray):
        if(data is None):
            print(f"{now} Cant continue with empty data")
            return
        # print(f"{now()} Sending tensor with {data.size} elements")
        # msg = data.flatten().tobytes()
        try:
            print(f'{now()} Sending kafka msg to {self.TOPIC_NAME} topic')
            self.producer.send(self.TOPIC_NAME, value=data)
            self.producer.flush()
            print(f'{now()} Done sending')
        except:
            print(f"{now()} Unexpected error:", sys.exc_info())
    def run(self):
        date_to = datetime.utcnow()
        msg = np.random.randint(0, 100, (3,3))
        i = 0
        while(True):
            MESSAGE = {
                "type": "get_parameters",
                "payload": {
                    "paramters": 0,
                    "epochs": 4
                }
            }
            self.sendMsg(MESSAGE)    
            time.sleep(1)
            i =+ 1
    def init(self, server_address, options, verbose=False):
        self.sasl_mechanism = 'PLAIN'
        self.security_protocol = 'SASL_PLAINTEXT'

        self.DEFAULT_TIMEOUT=5000
        self.SLEEP_TIME = int(os.environ.get("SLEEP_TIME", 300))
        self.MAX_SIZE = 104857600

        # Kafka producer
        self.KAFKA_BROKER_URL = (
            server_address
            if server_address
            else "localhost:9092"
        )
        self.TOPIC_NAME = (
            options['topic_name'] if "topic_name" in options else "test"
        )

        self.KAFKA_USERNAME = (
            os.environ.get("KAFKA_USERNAME") if os.environ.get("KAFKA_USERNAME") else ""
        )
        self.KAFKA_PASSWORD = (
            os.environ.get("KAFKA_PASSWORD") if os.environ.get("KAFKA_PASSWORD") else ""
        )    

if __name__ == "__main__":
    service = MsgSender(
        '10.138.0.6:9092',
        options={
            "max_send_message_length": KAFKA_MAX_SIZE,
            "max_receive_message_length": KAFKA_MAX_SIZE,
            "topic_name": 'enginner_x_train'
        },
    )
    print(f"{now()} Starting producer test at {service.KAFKA_BROKER_URL}")
    service.run()
    # time.sleep(10) #adding sleep here just to be able to see the logs after running.