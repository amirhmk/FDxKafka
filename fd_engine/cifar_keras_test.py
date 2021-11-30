import sys, os
sys.path.insert(0, os.getcwd())

import tensorflow as tf
import argparse
import flwr as fl
import yaml

cfg = os.path.join(os.getcwd(), 'env.yaml')
with open(cfg, 'r') as f:
    configparam = yaml.load(f,Loader=yaml.FullLoader)

os.environ['KAFKA_USERNAME'] = configparam['config']['KAFKA_USERNAME']
os.environ['KAFKA_PASSWORD'] = configparam['config']['KAFKA_PASSWORD']

def main(kafka_server,clientid=None):
# Load and compile Keras model
    model = tf.keras.applications.MobileNetV2((32, 32, 3), classes=10, weights=None)
    model.compile("adam", "sparse_categorical_crossentropy", metrics=["accuracy"])

    # Load CIFAR-10 dataset
    (x_train, y_train), (x_test, y_test) = tf.keras.datasets.cifar10.load_data()

    # Define Flower client
    class CifarClient(fl.client.NumPyClient):
        def get_parameters(self):  # type: ignore
            return model.get_weights()

        def fit(self, parameters, config):  # type: ignore
            model.set_weights(parameters)
            model.fit(x_train, y_train, epochs=1, batch_size=32, steps_per_epoch=3)
            return model.get_weights(), len(x_train)

        def evaluate(self, parameters, config):  # type: ignore
            model.set_weights(parameters)
            loss, accuracy = model.evaluate(x_test, y_test)
            return len(x_test), loss, accuracy
        # Not sure why we need this...
        def get_properties(self, config):
            return config
    # Start client
    fl.client.start_numpy_kafka_client(kafka_server, client=CifarClient(), clientid=clientid)
if __name__ == "__main__":
    a = argparse.ArgumentParser()
    a.add_argument("--broker", help="host_port of kafka broker")
    args = a.parse_args()
    print(args)

    main(args.broker)