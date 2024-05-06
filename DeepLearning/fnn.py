#Import modules
import os, sys, time
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

        layers_list.append(layers.Dense(output_shape, activation="linear"))
        
        self.model = keras.Sequential(layers_list, name="FNN")
        self.model.summary()

        # self.model.compile(loss="mean_squared_error", optimizer=keras.optimizers.Adam(learning_rate=0.0005), metrics=["mae", "mse"])
        self.model.compile(loss="mean_absolute_error", optimizer=keras.optimizers.Adam(learning_rate=0.0005), metrics=["mae", "mse"])

    def trainModel(self, x_trn, y_trn, batch_size, epochs):
        
        self.batch_size = batch_size
        self.epochs = epochs

        self.history = self.model.fit(x_trn, y_trn, batch_size=self.batch_size, epochs=self.epochs)

    def getLossAndAccuracy(self):

        trn_loss = np.array(self.history.history["loss"])
        trn_mae = np.array(self.history.history["mae"])

        return trn_loss, trn_mae
    
    def plotLossAndAccuracy(self, trn_loss, trn_acc):


        fig, ax1 = plt.subplots()
        ax2 = ax1.twinx()
        ax1.plot(np.arange(self.epochs)+1, trn_loss, 'b-', label = "Loss")
        ax2.plot(np.arange(self.epochs)+1, trn_acc, 'g-', label = "MAE")

        ax1.set_xlabel("Epochs")
        ax1.set_ylabel("Training Loss")
        ax2.set_ylabel("Training MAE")

        fig.legend()
        plt.show(block=True)

    def evaluateModel(self, x_tst, y_tst):

        score = self.model.evaluate(x_tst, y_tst, verbose=0)
        print("Test loss:", score[0])
        print("Test MAE:", score[1])

        return score
    
    def testTimePrediction(self, sample):
        start_time = time.time()
        prediction = self.model.predict(sample)
        end_time = time.time()
        print(f"Prediction time: {end_time - start_time} seconds")
        return (end_time - start_time), prediction
    
def getInfoFromData(data, train_data, train_label, test_data, test_label):
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
    
def getDataNormalizeAndSplit(cut_data_set=None, display_info=None):
    test_size=0.3

    # Step 1: Read the CSV file
    data = pd.read_csv(os.path.join('DeepLearning','tx', 'data' + '.csv'))

    data = data.sample(frac=1).reset_index(drop=True)

    if cut_data_set != None:
        data = data.sample(frac=cut_data_set).reset_index(drop=True)

    # Step 2: Split the data into training and testing sets and shuffle it
    train_data, test_data = train_test_split(data, test_size=test_size, random_state=42, shuffle=True)

    # Optionally, you can reset the index of the DataFrames
    train_data.reset_index(drop=True, inplace=True)
    test_data.reset_index(drop=True, inplace=True)

    # Step 3: Split the training and testing data into features and labels
    train_label = train_data['label']  # Extract the target variable for training
    train_data = train_data.drop('label', axis=1)  # Remove the target variable from the training features

    test_label = test_data['label']  # Extract the target variable for testing
    test_data = test_data.drop('label', axis=1)  # Remove the target variable from the testing features

    # Step 4: Normalize the data using maximum values of each feature
    max_values = train_data.max()
    train_data_normalized = train_data / max_values
    test_data_normalized = test_data / max_values

    # Normalize the target variable using maximum value
    max_label = train_label.max()
    train_label_normalized = train_label / max_label
    test_label_normalized = test_label / max_label

    # Print lengths of train_data and test_data
    print("Length of train_data:", len(train_data))
    print("Length of test_data:", len(test_data))

    print("Maximum values of each feature:")
    print(max_values)
    print("Maximum value of the target variable:")
    print(max_label)

    if display_info != None:
        getInfoFromData(data, train_data, train_label, test_data, test_label)
        # getInfoFromData(data, train_data_normalized, train_label_normalized, test_data_normalized, test_label_normalized)

    return train_data_normalized, train_label_normalized, test_data_normalized, test_label_normalized

def firstSimpleModel():
    x_train, y_train, x_test, y_test = getDataNormalizeAndSplit()

    model = FnnMode(input_shape=3, num_layers=3, neurons_per_layer=[512, 256, 32], activation_function='relu')
    model.trainModel(x_train, y_train, batch_size=512, epochs=5)
    trn_loss, trn_mae = model.getLossAndAccuracy()
    print(f"Training loss: {trn_loss}")
    print(f"Training MAE: {trn_mae}")

    model.plotLossAndAccuracy(trn_loss=trn_loss, trn_acc=trn_mae)

    model.evaluateModel(x_test, y_test)

def evaluateBestModel():
    # Define the sweep parameters
    num_layers_list = [2, 3, 4, 5]
    neurons_per_layer_list = [[256, 32], [512, 256, 32], [512, 256, 128, 32], [512, 256, 128, 64, 16]]

    x_train, y_train, x_test, y_test = getDataNormalizeAndSplit()

    # Create a list to store all the models
    all_models = []

    # Train each model and store it in the list
    for num_layers, neurons_per_layer in zip(num_layers_list, neurons_per_layer_list):
        print(f"Creating model for Num Layers: {num_layers} and Num Neurons: {neurons_per_layer}")
        # Create and train the model
        model = FnnMode(input_shape=3, num_layers=num_layers, neurons_per_layer=neurons_per_layer, activation_function='relu')
        model.trainModel(x_train, y_train, batch_size=256, epochs=6)

        # filename = f"saved_models/model_{num_layers}layers_{'_'.join(map(str, neurons_per_layer))}.h5"
        # model.saveModel(filename)

        all_models.append(model)

    # Plot loss and MAE for each model
    plt.figure(figsize=(2, 2))
    for i, (model, neurons_per_layer) in enumerate(zip(all_models, neurons_per_layer_list)):
        # Get loss and MAE
        trn_loss, trn_mae = model.getLossAndAccuracy()
        
        # Plot loss
        label = f'Model {i+1}: {len(neurons_per_layer_list)} layers, {neurons_per_layer} neurons/layer'
        plt.plot(np.arange(model.epochs) + 1, trn_loss, label=label)

        # Plot MAE
        plt.plot(np.arange(model.epochs) + 1, trn_mae, label=f'{label} - MAE', linestyle='--')

    plt.xlabel('Epochs')
    plt.ylabel('Training Metrics')
    plt.title('Training Loss and MAE for Different Models')
    plt.legend()
    plt.show()

    for i, (model, neurons_per_layer) in enumerate(zip(all_models, neurons_per_layer_list)):
        print(f"For model with Layers: {len(neurons_per_layer)} and Neurons: {neurons_per_layer}")
        trn_loss, trn_mae = model.getLossAndAccuracy()
        print(f"Training loss: {trn_loss}")
        print(f"Training MAE: {trn_mae}")
        model.evaluateModel(x_test, y_test)

def minimizeDataSet():
    num_layers = 3
    neurons_per_layer = [512, 256, 32]
    test_mae = sys.float_info.min
    cut_data_set = 1

    while test_mae < 0.1:
        x_train, y_train, x_test, y_test = getDataNormalizeAndSplit(cut_data_set=cut_data_set)

        model = FnnMode(input_shape=3, num_layers=num_layers, neurons_per_layer=neurons_per_layer, activation_function='relu')
        model.trainModel(x_train, y_train, batch_size=256, epochs=6)
        score = model.evaluateModel(x_test, y_test)
        print(f"For {cut_data_set*100}% of the dataset, the Loss achieved is: {score[0]} and the MAE: {score[1]}")

        if cut_data_set <= 0.1:
            cut_data_set = cut_data_set-0.05
        else:
            cut_data_set = cut_data_set-0.1

def testSpeedPerformance():
    num_layers = 3
    neurons_per_layer = [512, 256, 32]
    n_tests = 1000
    time_mean = []
    t = 0

    x_train, y_train, x_test, y_test = getDataNormalizeAndSplit()

    model = FnnMode(input_shape=3, num_layers=num_layers, neurons_per_layer=neurons_per_layer, activation_function='relu')
    model.trainModel(x_train, y_train, batch_size=256, epochs=6)
    # score = model.evaluateModel(x_test, y_test)
    sample = x_test.iloc[[0]]

    while n_tests > 0:
        
        sample = x_test.iloc[[n_tests]]
        t, prediction = model.testTimePrediction(sample=sample)
        time_mean.append(t)

        n_tests -= 1

    print(f"Average time to perform a prediction: {sum(time_mean)/len(time_mean)} seconds")

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