import sys, os
sys.path.insert(0, os.getcwd())
os.environ['KMP_DUPLICATE_LIB_OK']='True'

import numpy as np
import flwr as fl
from logging import INFO
import fd_engine.model as model
import fd_engine.dataset as dataset
import os
import yaml

from flwr.common.logger import log

cfg = os.path.join(os.getcwd(), 'env.yaml')
with open(cfg, 'r') as f:
    configparam = yaml.load(f,Loader=yaml.FullLoader)

os.environ['KAFKA_USERNAME'] = configparam['config']['KAFKA_USERNAME']
os.environ['KAFKA_PASSWORD'] = configparam['config']['KAFKA_PASSWORD']

class CifarClient(fl.client.NumPyClient):
    def __init__(self, model, x_train, y_train, x_test, y_test):
        self.model = model
        self.x_train, self.y_train = x_train, y_train
        self.x_test, self.y_test = x_test, y_test

    # Not sure why we need this...
    def get_properties(self, config):
        return super().get_properties(config)

    def get_parameters(self):
        return self.model.get_weights()

    def fit(self, parameters, config):
        self.model.set_weights(parameters)
        self.model.fit(self.x_train, self.y_train, epochs=1, batch_size=32)
        return self.model.get_weights(), len(self.x_train), {}

    def evaluate(self, parameters, config):
        self.model.set_weights(parameters)
        loss, accuracy = self.model.evaluate(self.x_test, self.y_test)
        return loss, len(self.x_test), {"accuracy": accuracy}


def main(client_id, broker=None, channel='kafka'):
    """Create model, load data, define Flower client, start Flower client."""
    # Start client
    SERVER_ADDRESS = "34.105.38.178:9091"
    if broker is None:
	    broker = SERVER_ADDRESS

    print(f"Using broker at {broker}")
    m = model.create_keras_model()
    m.compile("adam", "binary_crossentropy", metrics=["accuracy"])
    (x_train, y_train), (x_test, y_test) = dataset.load_partition(np.random.randint(0,10))
    client = CifarClient(m, x_train, y_train, x_test, y_test)

    if channel == "kafka":
        log(INFO, "Using Kafka Client")
        fl.client.start_kafka_client(broker, client=client, clientid=client_id)
    else:
        log(INFO, "Using gRPC Client")
        fl.client.start_numpy_client(broker, client=client)


if __name__ == "__main__":
    main(client_id=2, broker="35.203.161.106:8081", channel='gRPC')
    # main(client_id=2, broker="34.105.38.178:9091", channel='kafka')
