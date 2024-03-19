#Import modules
import numpy as np
import matplotlib.pyplot as plt
import tensorflow as tf
from tensorflow import keras
from keras import layers

class FnnMode():

    def __init__(self, input_shape=None):

        if input_shape == None:
            input_shape = (4,)
        else:
            input_shape = (input_shape,)
        output_shape  = 1

        self.model = keras.Sequential([layers.Input(shape = input_shape),
                                layers.Flatten(),
                                layers.Dense(512, "relu"),
                                layers.Dense(256, "relu"),
                                layers.Dense(128, "relu"),
                                layers.Dense(64, "relu"),
                                layers.Dense(32, "relu"),
                                layers.Dense(output_shape, "linear")],name="FNN")
        self.model.summary()

        self.model.compile(loss="mean_squared_error", optimizer="adam", metrics=["mae"])

    def trainModel(self, x_trn, y_trn):
        
        self.batch_size = 256
        self.epochs = 10

        self.history = self.model.fit(x_trn, y_trn, batch_size=self.batch_size, epochs=self.epochs)

    def getLossAndAccuracy(self):

        trn_loss = np.array(self.history.history["loss"])
        trn_acc = np.array(self.history.history["accuracy"])

        return trn_loss, trn_acc
    
    def plotLossAndAccuracy(self, trn_loss, trn_acc):


        fig, ax1 = plt.subplots()
        ax2 = ax1.twinx()
        ax1.plot(np.arange(self.epochs)+1, trn_loss, 'b-', label = "Loss")
        ax2.plot(np.arange(self.epochs)+1, 100*trn_acc, 'g-', label = "Acc.")

        ax1.set_xlabel("Epochs")
        ax1.set_ylabel("Training Loss")
        ax2.set_ylabel("Training Accuracy")

        fig.legend()

    def evaluateModel(self, x_tst, y_tst):

        score = self.model.evaluate(x_tst, y_tst, verbose=0)
        print("Test loss:", score[0])
        print("Test accuracy:", score[1]*100)

        return score