import flwr as fl
import tensorflow as tf

import model
import dataset
# # import multiprocessing as mp
# # from flower_helper import train, test

class CifarClient(fl.client.NumPyClient):
    def __init__(self, model, data):
        # model = tf.keras.applications.MobileNetV2((32, 32, 3), classes=10, weights=None)
        # model.compile("adam", "sparse_categorical_crossentropy", metrics=["accuracy"])
        self.data = data
        self.model = model
        # (self.x_train, self.y_train), (self.x_test, self.y_test) = tf.keras.datasets.cifar10.load_data()

    def get_parameters(self):
        return self.model.get_weights()

    def fit(self, parameters, config):
        # print("nvm it's this one", parameters)
        self.model.set_weights(parameters)
        self.model.fit(self.data, epochs=1, batch_size=32, steps_per_epoch=3)
        return self.model.get_weights(), len(self.x_train), {}

    def evaluate(self, parameters, config):
        # print("helllo", parameters)
        self.model.set_weights(parameters)
        loss, accuracy = self.model.evaluate(self.data)
        return loss, len(self.x_test), {"accuracy": accuracy}


def main():
    """Create model, load data, define Flower client, start Flower client."""
    # Set the start method for multiprocessing in case Python version is under 3.8.1
    # mp.set_start_method("spawn")

    # Start client
    # TODO: MOdify here to change server address
    SERVER_ADDRESS = "[::]:8081"
    m = model.create_keras_model()
    m.compile("adam", "binary_crossentropy", metrics=["accuracy"])
    DATASET_PATH = "data/train"
    data = dataset.get_dataset(DATASET_PATH)
    fl.client.start_numpy_client(SERVER_ADDRESS, client=CifarClient(m, data))


if __name__ == "__main__":
    main()
