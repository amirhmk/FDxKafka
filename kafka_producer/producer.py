import sys
import os
import time
import json
from datetime import datetime
from kafka import KafkaProducer
import numpy as np
from logging import INFO,DEBUG

now = lambda : str(datetime.now())

KAFKA_MAX_SIZE = 104857600

SERVER_ADDRESS = '10.138.0.6:9092'

import json
from json import JSONEncoder
import numpy

class NumpyArrayEncoder(JSONEncoder):
    def default(self, obj):
        if isinstance(obj, numpy.ndarray):
            return obj.tolist()
        return JSONEncoder.default(self, obj)

class MsgSender:
    def __init__(self, server_address, options):
        self.init(server_address, options)
        self.producer = KafkaProducer(bootstrap_servers = self.KAFKA_BROKER_URL,
                        #  sasl_plain_username = self.KAFKA_USERNAME,
                        #  sasl_plain_password = self.KAFKA_PASSWORD,
                         security_protocol = "PLAINTEXT",
                        #  sasl_mechanism = self.sasl_mechanism,
                        #  value_serializer=lambda x: x.encode("utf8"),
                        #  value_serializer=lambda x: bytes(str(x), 'utf-8'),
                        #  value_serializer=lambda v: json.dumps(v, cls=NumpyArrayEncoder).encode('utf-8'),
                         api_version=(0, 11, 5),
                         max_request_size=self.MAX_SIZE,
                         retries=5,
                         max_block_ms=self.DEFAULT_TIMEOUT)


    def sendMsg(self, data, topic_name : str=None):
        if(data is None):
            self.log(INFO, "Cant continue with empty data")
            return
        if topic_name is None:
            topic_name = self.TOPIC_NAME
        try:
            self.log(INFO, f'Sending kafka {len(data)} bytes to {topic_name} topic')
            self.producer.send(topic_name, value=data)
            self.producer.flush()
            self.log(DEBUG, 'Done sending')
        except:
            self.log(INFO, f"Unexpected error: {sys.exc_info()}")
    def close(self):
        self.log(DEBUG, 'Closing kafka producer')
        self.producer.close()
    def run(self):
        date_to = datetime.utcnow()
        parameter_1 = np.random.randint(0, 100, (3072,10))
        parameter_2 = np.zeros((10,))
        i = 0
        MESSAGE = {
                "type": "fit_ins",
                "server_address": SERVER_ADDRESS,
                "max_send_message_length": KAFKA_MAX_SIZE,
                "max_receive_message_length": KAFKA_MAX_SIZE,
                "topic_name": "enginner_x_train_progress",
                "parameters": {
                    "tensors": [parameter_1, parameter_2],
                    "tensor_type": "numpy.ndarray"
                },
                "local_epochs": 4,
                "batch_size": 16
            }
        while(True):
            print("lets check this", json.dumps(MESSAGE, cls=NumpyArrayEncoder))
            self.sendMsg(MESSAGE)    
            # self.sendMsg(json.dumps(MESSAGE, cls=NumpyArrayEncoder))    
            time.sleep(1)
            i =+ 1
            # MESSAGE = {
            #     "type": "get_parameters",
            #     "payload": {
            #         "paramters": 0,
            #         "epochs": 4
            #     }
            # }
            
    def init(self, server_address, options, verbose=False):
        self.log = options['log']
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
        SERVER_ADDRESS,
        options={
            "max_send_message_length": KAFKA_MAX_SIZE,
            "max_receive_message_length": KAFKA_MAX_SIZE,
            "topic_name": 'enginner_x_train'
        },
    )
    print(f"{now()} Starting producer test at {service.KAFKA_BROKER_URL}")
    service.run()
    # time.sleep(10) #adding sleep here just to be able to see the logs after running.