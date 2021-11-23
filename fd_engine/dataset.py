import tensorflow as tf


def image_loader(dataset_path, batch_size=32, num_classes=2, image_size=256):
  """
  Return a tf.data dataset object, by applying a 20 deg rotation and other
  preprocessing steps.
  """
  img_gen = tf.keras.preprocessing.image.ImageDataGenerator(rescale=1./255, rotation_range=20)

  ds = tf.data.Dataset.from_generator(
    lambda: img_gen.flow_from_directory(dataset_path), 
    output_types=(tf.float32, tf.float32), 
    output_shapes=([batch_size,image_size,image_size,3], [batch_size,num_classes])
  )

  return ds

def get_dataset(dataset_path):
  ds = image_loader(dataset_path)
  augmented_train_ds = ds.map(lambda x, y: (x, y))
  return augmented_train_ds

def load_partition(idx: int):
    """Load 1/10th of the training and test data to simulate a partition."""
    assert idx in range(10)
    (x_train, y_train), (x_test, y_test) = tf.keras.datasets.cifar10.load_data()

    res = (
        x_train[idx * 5000 : (idx + 1) * 5000].reshape((-1, 3072)),
        y_train[idx * 5000 : (idx + 1) * 5000],
    ), (
        x_test[idx * 1000 : (idx + 1) * 1000].reshape((-1, 3072)),
        y_test[idx * 1000 : (idx + 1) * 1000],
    )
    return res


if __name__ == "__main__":
  get_dataset("data/train")
