import tensorflow as tf

def create_keras_model():
  return tf.keras.models.Sequential([
      tf.keras.layers.InputLayer(input_shape=(784,)),
      tf.keras.layers.Dense(10, kernel_initializer='zeros'),
      tf.keras.layers.Softmax(),
  ])

  # return tf.keras.models.Sequential([
  #     tf.keras.layers.InputLayer(input_shape=(784,)),
  #     tf.keras.layers.Conv2D(filters=32, kernel_size=3, strides=(2, 2), activation='relu'),
  #     tf.keras.layers.Conv2D(filters=64, kernel_size=3, strides=(2, 2), activation='relu'),
  #     tf.keras.layers.Flatten(),
  #     tf.keras.layers.Dense(9)
  # ])

# def get_model_fn(preprocessed_example_dataset):
#   # We _must_ create a new model here, and _not_ capture it from an external
#   # scope. TFF will call this within different graph contexts.
#   def model_fn():
#     keras_model = create_keras_model()
#     return tff.learning.from_keras_model(
#         keras_model,
#         input_spec=preprocessed_example_dataset.element_spec,
#         loss=tf.keras.losses.SparseCategoricalCrossentropy(),
#         metrics=[tf.keras.metrics.SparseCategoricalAccuracy()])
#   return model_fn