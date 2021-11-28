import os
import threading
from kafka import KafkaConsumer
from datetime import datetime
from threading import Thread
import queue

KAFKA_MAX_SIZE = 104857600

now = lambda : str(datetime.now())


class StoppableThread(Thread):
    """Thread class with a stop() method. The thread itself has to check
    regularly for the stopped() condition."""

    def __init__(self,  *args, **kwargs):
        super(StoppableThread, self).__init__(*args, **kwargs)
        self._stop_event = threading.Event()

    def stop(self):
        self._stop_event.set()

    def stopped(self):
        return self._stop_event.is_set()

class MsgReceiver(StoppableThread):
    def __init__(self, server_address, options=None) -> None:
        super(MsgReceiver,self).__init__(name='MsgReceiverThread')
        self.init(server_address, options)
        print(f"{now()} Setting up Kafka consumer at {self.KAFKA_BROKER_URL}")
        self.consumer = KafkaConsumer(self.TOPIC_NAME, bootstrap_servers=self.KAFKA_BROKER_URL,
                                sasl_plain_username = self.KAFKA_USERNAME,
                                sasl_plain_password = self.KAFKA_PASSWORD,
                                security_protocol = self.security_protocol,
                                sasl_mechanism = self.sasl_mechanism)
        self.q = queue.Queue()

    def init(self, server_address, options, verbose=False):
        self.sasl_mechanism = 'PLAIN'
        self.security_protocol = 'SASL_PLAINTEXT'

        self.DEFAULT_TIMEOUT=5000
        self.SLEEP_TIME = int(os.environ.get("SLEEP_TIME", 300))
        self.MAX_SIZE = 104857600

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
    
    def getNextMsg(self, block=True, timeout=None):
        try:
            return self.q.get(block, timeout)
        except: #timeout empty exception
            return None
    
    def getNextMsgIterator(self):
        yield self.q.get(True, None)

    def run(self):
        while not self.stopped():
            for msg in self.consumer:
                self.q.put(msg)

    def close(self):
        # TODO
        # stop thread, consumer
        # self.thread.stop()
        self.consumer.close()
        pass

if __name__ == "__main__":
    #start receiver in a new thread
    receiver = MsgReceiver(
        '10.138.0.6:9092',
        options={
            "max_send_message_length": KAFKA_MAX_SIZE,
            "max_receive_message_length": KAFKA_MAX_SIZE,
            "topic_name": 'enginner_x_train_progress'
        },
    )
    receiver.start()

    #get messages received
    while(True):
        newdata = receiver.getNextMsg(block=True) #blocking or non blocking
        if newdata:
            print(f'{now()} Client received: {newdata}')
