import tensorflow as tf
import collections

NUM_CLIENTS = 10
NUM_EPOCHS = 5
BATCH_SIZE = 20
SHUFFLE_BUFFER = 100
PREFETCH_BUFFER = 10

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

if __name__ == "__main__":
  get_dataset("data/train")
