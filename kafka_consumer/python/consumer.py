import os, sys
from kafka import KafkaConsumer, KafkaProducer
from datetime import datetime
from threading import Thread
import queue
import numpy as np

now = lambda : str(datetime.now())

class MsgReceiver(Thread):
    def __init__(self) -> None:
        super(MsgReceiver,self).__init__(name='MsgReceiverThread')
        self.init()
        print(f"{now()} Setting up Kafka consumer at {self.KAFKA_BROKER_URL}")
        self.consumer = KafkaConsumer(self.TOPIC_NAME, bootstrap_servers=self.KAFKA_BROKER_URL,
                                sasl_plain_username = self.KAFKA_USERNAME,
                                sasl_plain_password = self.KAFKA_PASSWORD,
                                security_protocol = self.security_protocol,
                                sasl_mechanism = self.sasl_mechanism)
        self.q = queue.Queue()

    def init(self, verbose=None):
        self.sasl_mechanism = 'PLAIN'
        self.security_protocol = 'SASL_PLAINTEXT'

        self.DEFAULT_TIMEOUT=5000
        self.SLEEP_TIME = int(os.environ.get("SLEEP_TIME", 300))
        self.MAX_SIZE = 104857600

        self.KAFKA_BROKER_URL = (
            os.environ.get("KAFKA_BROKER_URL")
            if os.environ.get("KAFKA_BROKER_URL")
            else "localhost:9092"
        )
        self.TOPIC_NAME = (
            os.environ.get("TOPIC_NAME") if os.environ.get("TOPIC_NAME") else "test"
        )

        self.KAFKA_USERNAME = (
            os.environ.get("KAFKA_USERNAME") if os.environ.get("KAFKA_USERNAME") else ""
        )
        self.KAFKA_PASSWORD = (
            os.environ.get("KAFKA_PASSWORD") if os.environ.get("KAFKA_PASSWORD") else ""
        )

    def getNextMsg(self, block=True, timeout=None) -> np.ndarray:
        return self.q.get(block, timeout)

    def run(self):
        print(f'{now()} Waiting for msg...')
        for msg in self.consumer:
            # msg = msg.value.decode('utf-8')
            received = np.frombuffer(msg.value, dtype=float)
            #gonna have to agree on a size or send it too.
            received = np.reshape(received, (3,3))
            print(f"{now()} Message received a {received.shape} array")
            self.q.put(received)

if __name__ == "__main__":
    #start receiver in a new thread
    receiver = MsgReceiver()
    receiver.start()

    #get messages received
    while(True):
        newdata = receiver.getNextMsg(block=True) #blocking or non blocking
        print(f'{now()} Client received: {newdata}')

    print("Bye-Bye")
