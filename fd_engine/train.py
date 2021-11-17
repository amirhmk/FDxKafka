import tensorflow as tf

import dataset
import model

def train(dataset_path):
    data = dataset.get_dataset(dataset_path)
    m = model.create_keras_model()
    m.compile("adam", "binary_crossentropy", metrics=["accuracy"])
    
    history = m.fit(data)

if __name__ == "__main__":
    train("data/train")