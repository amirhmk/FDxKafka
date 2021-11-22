import flwr as fl
import tensorflow as tf

import model
import dataset

import os
try:
    user_paths = os.environ['PYTHONPATH'].split(os.pathsep)
except KeyError:
    user_paths = []

print('PYTHONPATH', user_paths, fl.common)

class CifarClient(fl.client.NumPyClient):
    def __init__(self, model, data):
        self.model = model
        self.data = data

    # Not sure why we need this...
    def get_properties(self, config):
        return super().get_properties(config)

    def get_parameters(self):
        return self.model.get_weights()

    def fit(self, parameters, config):
        self.model.set_weights(parameters)
        self.model.fit(self.data, epochs=1, batch_size=32, steps_per_epoch=3)
        return self.model.get_weights(), 32, {}

    def evaluate(self, parameters, config):
        self.model.set_weights(parameters)
        # TODO: Change to valid data
        loss, accuracy = self.model.evaluate(self.data)
        return loss, 32, {"accuracy": accuracy}


def main():
    """Create model, load data, define Flower client, start Flower client."""
    # Start client
    SERVER_ADDRESS = "[::]:8081"
    m = model.create_keras_model()
    m.compile("adam", "binary_crossentropy", metrics=["accuracy"])
    DATASET_PATH = "data/train"
    data = dataset.get_dataset(DATASET_PATH)
    # TODO: partition data into train/valid/test
    fl.client.start_kafka_client(SERVER_ADDRESS, client=CifarClient(m, data))


if __name__ == "__main__":
    main()
