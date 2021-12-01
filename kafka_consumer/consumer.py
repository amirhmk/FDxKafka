import os
import threading
from kafka import KafkaConsumer
from datetime import datetime
from threading import Thread
import queue
from logging import INFO, DEBUG
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
        # raise Exception('Stop!')

    def stopped(self):
        return self._stop_event.is_set()

class MsgReceiver(StoppableThread):
    def __init__(self, server_address, options=None) -> None:
        super(MsgReceiver,self).__init__(name='MsgReceiverThread')
        self.init(server_address, options)
        self.log(INFO, f"Setting up Kafka consumer at {self.KAFKA_BROKER_URL}")
        self.consumer : KafkaConsumer = KafkaConsumer(self.TOPIC_NAME, bootstrap_servers=self.KAFKA_BROKER_URL,
                                # sasl_plain_username = self.KAFKA_USERNAME,
                                # sasl_plain_password = self.KAFKA_PASSWORD,
                                security_protocol = "PLAINTEXT",
                                auto_offset_reset = "latest",
                                group_id = str(options['cid']),
                                client_id = str(options['cid']),
                                api_version = (0, 9)
                                # sasl_mechanism = self.sasl_mechanism
                                )
        self.q = queue.Queue()

    def init(self, server_address, options, verbose=False):
        self.log = options['log']
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
            self.log(INFO, f"Getting next msg from {self.TOPIC_NAME} with block={block} and timeout={timeout}")
            return self.q.get(block, timeout)
        except: #timeout empty exception
            self.log(INFO, f"Error getting next msg from {self.TOPIC_NAME}")
            return None
        finally:
            self.log(INFO, f"Done getting next msg from {self.TOPIC_NAME}")

    def run(self):
        while not self.stopped():
            try:
                self.log(DEBUG, 'Receiver waiting for next msg')
                for msg in self.consumer:
                    self.log(DEBUG, 'Got new msg!')
                    self.q.put(msg.value)
            except Exception as e:
                self.log(DEBUG, 'Receiver thread interrupted', e)
            if self.stopped():
                break
        self.log(DEBUG, 'Receiver thread stopped')
    def close(self):
        self.log(DEBUG, 'Closing connection for consumer')
        self.stop()
        self.consumer.close()
        self.stop()

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
