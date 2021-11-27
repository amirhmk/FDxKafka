import tensorflow as tf
import tensorflow_federated as tff

import dataset
import model
import client_kafka
import helper

def get_iterative_process(preprocessed_example_dataset):
    iterative_process = tff.learning.build_federated_averaging_process(
        model.get_model_fn(preprocessed_example_dataset),
        client_optimizer_fn=lambda: tf.keras.optimizers.SGD(learning_rate=0.02),
        server_optimizer_fn=lambda: tf.keras.optimizers.SGD(learning_rate=1.0)
    )
    return iterative_process

def train_tff():
    preprocessed_example_dataset = dataset.preprocess()
    federated_train_data = dataset.make_federated_data(emnist_train, sample_clients)

    iterative_process = get_iterative_process(preprocessed_example_dataset)
    NUM_ROUNDS = 11
    state = iterative_process.initialize()
    for round_num in range(2, NUM_ROUNDS):
        state, metrics = iterative_process.next(state, federated_train_data)
        print('round {:2d}, metrics={}'.format(round_num, metrics))

def train(dataset_path):
    pass
    # data = dataset.get_dataset(dataset_path)
    # emnist_train, emnist_test = tff.simulation.datasets.emnist.load_data()
    # m = model.create_keras_model()
    # m.compile("adam", "binary_crossentropy", metrics=["accuracy"])
    
    # history = m.fit(data)
    # print("history", history)


def run(client_id):
    model = tf.keras.applications.EfficientNetB0(
        input_shape=(32, 32, 3), weights=None, classes=10
    )
    model.compile("adam", "sparse_categorical_crossentropy", metrics=["accuracy"])

    # Load a subset of CIFAR-10 to simulate the local data partition
    (x_train, y_train), (x_test, y_test) = dataset.load_partition(client_id)

    # Start Flower client
    client = client_kafka.CifarClient(model, x_train, y_train, x_test, y_test)

    # parameters: List[np.ndarray] = helper.parameters_to_weights(model.get_weights())
    config = { 'batch_size': 32, 'local_epochs': 1 }
    w = client.fit(model.get_weights(), config)

    print(w.keys())
if __name__ == "__main__":
    # train("data/train")
    run(2)