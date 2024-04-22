#Import modules
import os
import numpy as np
import matplotlib.pyplot as plt
import tensorflow as tf
from tensorflow import keras
from keras import layers
import pandas as pd
from sklearn.model_selection import train_test_split

class FnnMode():

    def __init__(self, input_shape, num_layers, neurons_per_layer, activation_function):

        input_shape = (input_shape,)
        output_shape  = 1

        layers_list = [layers.Input(shape=input_shape)]

        for layer_index in range(num_layers):
            layers_list.append(layers.Dense(neurons_per_layer[layer_index], activation=activation_function))

        layers_list.append(layers.Dense(output_shape, "linear"))
        
        self.model = keras.Sequential(layers_list, name="FNN")
        self.model.summary()

        self.model.compile(loss="mean_squared_error", optimizer="adam", metrics=["mae"])

    def trainModel(self, x_trn, y_trn, batch_size, epochs):
        
        self.batch_size = batch_size
        self.epochs = epochs

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
    
def getDataNormalizeAndSplit():
    # Step 1: Read the CSV file
    data = pd.read_csv(os.path.join('DeepLearning','tx', 'data' + '.csv'))

    # Step 2: Split the data into training and testing sets and shuffle it
    train_data, test_data = train_test_split(data, test_size=0.3, random_state=42, shuffle=True)

    # Optionally, you can reset the index of the DataFrames
    train_data.reset_index(drop=True, inplace=True)
    test_data.reset_index(drop=True, inplace=True)

    # Step 3: Split the training and testing data into features and labels
    train_label = train_data['label']  # Extract the target variable for training
    train_data = train_data.drop('label', axis=1)  # Remove the target variable from the training features

    test_label = test_data['label']  # Extract the target variable for testing
    test_data = test_data.drop('label', axis=1)  # Remove the target variable from the testing features

    """
    # Basic inspection of the DataFrame
    print(data.head())  # Display the first few rows
    print(data.info())   # Display column names, data types, and non-null counts
    print(data.describe())  # Display summary statistics for numerical columns

    print("Training data shape:", train_data.shape)
    print("Training label shape:", train_label.shape)
    print("Testing data shape:", test_data.shape)
    print("Testing label shape:", test_label.shape)

    print("Training label statistics:")
    print(train_label.describe())
    print("Testing label statistics:")
    print(test_label.describe())

    plt.hist(train_label, bins=20, alpha=0.5, label='Training Label')
    plt.hist(test_label, bins=20, alpha=0.5, label='Testing Label')
    plt.legend()
    plt.xlabel('Label')
    plt.ylabel('Frequency')
    plt.title('Distribution of Labels')
    plt.show(block=True)

    print("Training data statistics:")
    print(train_data.describe())
    print("Testing data statistics:")
    print(test_data.describe())

    print("Missing values in training data:")
    print(train_data.isnull().sum())
    print("Missing values in testing data:")
    print(test_data.isnull().sum())
    """

    return train_data, train_label, test_data, test_label

def firstSimpleModel():
    x_train, y_train, x_test, y_test = getDataNormalizeAndSplit()

    model = FnnMode(num_layers=5, neurons_per_layer=[512, 256, 128, 64, 1])
    model.trainModel(x_train, y_train, batch_size=256, epochs=10)
    model.evaluateModel()




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
        model.trainModel(x_train, y_train, batch_size=256, epochs=10)

        filename = f"saved_models/model_{num_layers}layers_{'_'.join(map(str, neurons_per_layer))}.h5"
        model.saveModel(filename)

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