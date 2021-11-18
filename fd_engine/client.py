import flwr as fl
import tensorflow as tf

import model
import dataset

class CifarClient(fl.client.NumPyClient):
    def __init__(self, model, data):
        self.data = data
        self.model = model

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
    fl.client.start_numpy_client(SERVER_ADDRESS, client=CifarClient(m, data))


if __name__ == "__main__":
    main()
