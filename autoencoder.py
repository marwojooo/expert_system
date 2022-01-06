from keras.layers import Dense, Conv2D, MaxPooling2D, UpSampling2D
from keras import Input, Model, Sequential
from tensorflow.keras.utils import Sequence

import numpy as np
import matplotlib.pyplot as plt
import system_info as s
import tensorflow as tf
def get_autoencoder():
    autoencoder = Sequential()
    autoencoder.add(Input(shape=(5,)))
    # enkoder
    autoencoder.add(Dense(50, activation="relu"))
    # wąskie gardło
    autoencoder.add(Dense(3, activation="relu"))
    # dekoder
    autoencoder.add(Dense(50, activation="relu"))
    autoencoder.add(Dense(5, activation="sigmoid"))

    autoencoder.compile(optimizer="adam", loss="mean_squared_error")
    return autoencoder

class DataGenerator(Sequence):
    "Generates data for Keras"

    def __init__(
        self,
        batch_size=1,
        dim=(5,1),
        iter=100,
    ):
        "Initialization"
        self.dim = dim
        self.batch_size = batch_size
        self.on_epoch_end()
        self.iter=iter
    def __len__(self):
        return self.iter

    def __getitem__(self, index):
        "Generate one batch of data"

        X = self.__data_generation()

        return X, X

    def on_epoch_end(self):
        "Updates indexes after each epoch"
        pass
        # self.indexes = np.arange(len(self.list_IDs))
        # if self.shuffle == True:
        #     np.random.shuffle(self.indexes)

    def __data_generation(self):
        X = np.empty((self.batch_size, *self.dim))
        info=s.SystemInfo()

        for i in range(self.batch_size):
            info.get_data()
            X[
                i,
            ] = info.get_params()
            # ] = [5.1, 62.0, 49, 0, 0.0]


        return X

def load_model():
    autoencoder = get_autoencoder()
    autoencoder.load_weights("models/tr")
    return autoencoder

def train_model():
    autoencoder=get_autoencoder()
    params = {
        "dim": (5,),
        "batch_size": 8,
    }
    training_generator = DataGenerator(iter=64, **params)
    validation_generator = DataGenerator(iter=8, **params)

    checkpoint_path = "models/tr"

    cp_callback = tf.keras.callbacks.ModelCheckpoint(
        filepath=checkpoint_path, save_weights_only=True, verbose=1
    )

    autoencoder.fit_generator(
        generator=training_generator,
        validation_data=validation_generator,
        use_multiprocessing=False,
        workers=1,
        epochs=10,
        callbacks=[cp_callback]
    )