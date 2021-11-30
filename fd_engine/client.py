import sys, os
sys.path.insert(0, os.getcwd())

import flwr as fl
import fd_engine.model as model
import fd_engine.dataset as dataset
import os
import yaml

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
        # Update local model parameters
        self.model.set_weights(parameters)

        # Get hyperparameters for this round
        batch_size: int = config["batch_size"]
        epochs: int = config["local_epochs"]

        # Train the model using hyperparameters from config
        history = self.model.fit(
            self.x_train,
            self.y_train,
            batch_size,
            epochs,
            validation_split=0.1,
        )

        # Return updated model parameters and results
        parameters_prime = self.model.get_weights()
        num_examples_train = len(self.x_train)
        results = {
            "loss": history.history["loss"][0],
            "accuracy": history.history["accuracy"][0],
            "val_loss": history.history["val_loss"][0],
            "val_accuracy": history.history["val_accuracy"][0],
        }
        return parameters_prime, num_examples_train, results

    def evaluate(self, parameters, config):
        # Update local model with global parameters
        self.model.set_weights(parameters)

        # Get config values
        steps: int = config["val_steps"]

        # Evaluate global model parameters on the local test data and return results
        loss, accuracy = self.model.evaluate(self.x_test, self.y_test, 32, steps=steps)
        num_examples_test = len(self.x_test)
        return loss, num_examples_test, {"accuracy": accuracy}


def main(client_id):
    """Create model, load data, define Flower client, start Flower client."""
    # Start client
    # SERVER_ADDRESS = "10.138.0.6:9092"
    SERVER_ADDRESS = "34.105.38.178:9091"
    m = model.create_keras_model()
    m.compile("adam", "binary_crossentropy", metrics=["accuracy"])
    (x_train, y_train), (x_test, y_test) = dataset.load_partition(client_id)
    fl.client.start_kafka_client(SERVER_ADDRESS, client=CifarClient(m, x_train, y_train, x_test, y_test))


if __name__ == "__main__":
    main(2)
