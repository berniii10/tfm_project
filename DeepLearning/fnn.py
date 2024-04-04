#Import modules
import numpy as np
import matplotlib.pyplot as plt
import tensorflow as tf
from tensorflow import keras
from keras import layers

class FnnMode():

    def __init__(self, input_shape=None, num_layers=None, neurons_per_layer=None, activation_functions=None):

        if input_shape == None:
            input_shape = (4,)
        else:
            input_shape = (input_shape,)
        output_shape  = 1

        if num_layers == None or neurons_per_layer == None or activation_functions == None:
            num_layers = 5
            neurons_per_layer = [512, 256, 128, 64, 1]
            activation_functions = ['relu']*6

        layers_list = [layers.Input(shape=input_shape)]

        for layer_index in range(num_layers):
            layers_list.append(layers.Dense(neurons_per_layer[layer_index], activation=activation_functions[layer_index]))

        layers_list.append(layers.Dense(output_shape, "linear"))
        
        self.model = keras.Sequential(layers_list, name="FNN")
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
    
"""
For the caller of the function:

# Define the sweep parameters
num_layers_list = [3, 4, 5, 6]
neurons_per_layer_list = [[512, 256, 1], [512, 256, 128, 1], [512, 256, 128, 64, 1], [512, 256, 128, 64, 32, 1]]

# Create a list to store all the models
all_models = []

# Train each model and store it in the list
for num_layers in num_layers_list:
    for neurons_per_layer in neurons_per_layer_list:
        # Create and train the model
        model = FnnMode(num_layers=num_layers, neurons_per_layer=neurons_per_layer)
        model.trainModel(x_train, y_train)
        all_models.append(model)

# Plot loss for each model
plt.figure(figsize=(10, 6))
for i, model in enumerate(all_models):
    # Get loss
    trn_loss, _ = model.getLossAndAccuracy()
    
    # Plot loss
    label = f'Model {i+1}: {model.model.count_params()} parameters'
    plt.plot(np.arange(model.epochs) + 1, trn_loss, label=label)

plt.xlabel('Epochs')
plt.ylabel('Training Loss')
plt.title('Training Loss for Different Models')
plt.legend()
plt.show()

"""