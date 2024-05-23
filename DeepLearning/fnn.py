#Import modules
import os, sys, time
import numpy as np
import matplotlib.pyplot as plt
import tensorflow as tf
from tensorflow import keras
from keras import layers
import pandas as pd
from view.common import *
from sklearn.model_selection import train_test_split

global min_values, max_values, min_label, max_label

num_layers_ = 4
neurons_per_layer_ = [512, 256, 128, 32]

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
    
    def testTimePrediction(self, sample, verbose=None):
        start_time = time.time()
        prediction = self.model.predict(sample, verbose=0)
        end_time = time.time()
        if verbose != None:
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
    
def getDataNormalizeAndSplit(tx_rx=None, cut_data_set=None, display_info=None, test_size=None):
    if test_size == None:
        test_size=0.3
    global min_values, max_values, min_label, max_label

    # Step 1: Read the CSV file
    if tx_rx == 'tx':
        data = pd.read_csv(os.path.join('DeepLearning','tx', 'data' + '.csv'))
    elif tx_rx == 'rx':
        data = pd.read_csv(os.path.join('DeepLearning','rx', 'data' + '.csv'))

    data = data.sample(frac=1).reset_index(drop=True)

    # Step 2: Split the data into training and testing sets and shuffle it
    train_data, test_data = train_test_split(data, test_size=test_size, random_state=42, shuffle=True)

    if cut_data_set != None:
        train_data = train_data.sample(frac=cut_data_set).reset_index(drop=True)

    # Calculate min and max values for each feature and label
    min_values = data.drop('label', axis=1).min()
    max_values = data.drop('label', axis=1).max()
    min_label = data['label'].min()
    max_label = data['label'].max()

    # Optionally, you can reset the index of the DataFrames
    train_data.reset_index(drop=True, inplace=True)
    test_data.reset_index(drop=True, inplace=True)

    # Step 3: Split the training and testing data into features and labels
    train_label = train_data['label']  # Extract the target variable for training
    train_data = train_data.drop('label', axis=1)  # Remove the target variable from the training features

    test_label = test_data['label']  # Extract the target variable for testing
    test_data = test_data.drop('label', axis=1)  # Remove the target variable from the testing features

    # Step 4: Normalize the data using maximum values of each feature
    # Step 4: Normalize the data using min-max normalization
    train_data_normalized = (train_data - min_values) / (max_values - min_values)
    test_data_normalized = (test_data - min_values) / (max_values - min_values)

    # Normalize the target variable using maximum value
    train_label_normalized = (train_label - min_label) / (max_label - min_label)
    test_label_normalized = (test_label - min_label) / (max_label - min_label)

    # Print lengths of train_data and test_data
    if cut_data_set != None:
        print(f"Using {cut_data_set*100}% of the dataset")

    print("Length of train_data:", len(train_data))
    print("Length of test_data:", len(test_data))

    print("Minimum values of each feature:")
    print(min_values)
    print("Maximum values of each feature:")
    print(max_values)
    print("Minimum value of the target variable:")
    print(min_label)
    print("Maximum value of the target variable:")
    print(max_label)

    if display_info != None:
        getInfoFromData(data, train_data, train_label, test_data, test_label)
        getInfoFromData(data, train_data_normalized, train_label_normalized, test_data_normalized, test_label_normalized)

    return train_data_normalized, train_label_normalized, test_data_normalized, test_label_normalized

def deNormalizeData(params, label, prediction):
    params = params.flatten()
    denormalized_params = params * (max_values - min_values) + min_values
    denormalized_label = label * (max_label - min_label) + min_label
    denormalized_prediction = prediction * (max_label - min_label) + min_label
    return denormalized_params, denormalized_label, denormalized_prediction
    # return params * max_values.values.reshape(1, -1), label * max_label, prediction * max_label

def firstSimpleModel():
    x_train, y_train, x_test, y_test = getDataNormalizeAndSplit()

    model = FnnMode(input_shape=3, num_layers=3, neurons_per_layer=[512, 256, 32], activation_function='relu')
    model.trainModel(x_train, y_train, batch_size=512, epochs=5)
    trn_loss, trn_mae = model.getLossAndAccuracy()
    print(f"Training loss: {trn_loss}")
    print(f"Training MAE: {trn_mae}")

    model.plotLossAndAccuracy(trn_loss=trn_loss, trn_acc=trn_mae)

    model.evaluateModel(x_test, y_test)

def evaluateBestModel(tx_rx):
    # Define the sweep parameters
    num_layers_list = [2, 3, 4, 5, 6]
    neurons_per_layer_list = [[256, 32], [512, 256, 32], [512, 256, 128, 32], [512, 256, 128, 64, 16], [512, 256, 128, 64, 32, 16]]

    x_train, y_train, x_test, y_test = getDataNormalizeAndSplit(tx_rx=tx_rx)

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
        label = f'Model {i+1}: {len(neurons_per_layer)} layers, {neurons_per_layer} neurons/layer'
        plt.plot(np.arange(model.epochs) + 1, trn_loss, label=label)

        # Plot MAE
        plt.plot(np.arange(model.epochs) + 1, trn_mae, label=f'{label} - MAE', linestyle='--')

    plt.xlabel('Epochs', fontsize=16)
    plt.ylabel('Training Metrics', fontsize=16)
    plt.title('Training Loss and MAE for Different Models', fontsize=32)
    plt.xticks(fontsize=16)
    plt.yticks(fontsize=16)
    plt.legend(fontsize=14)
    plt.show(block=True)

    for i, (model, neurons_per_layer) in enumerate(zip(all_models, neurons_per_layer_list)):
        print(f"For model with Layers: {len(neurons_per_layer)} and Neurons: {neurons_per_layer}")
        trn_loss, trn_mae = model.getLossAndAccuracy()
        print(f"Training loss: {trn_loss}")
        print(f"Training MAE: {trn_mae}")
        model.evaluateModel(x_test, y_test)

def testSpeedAndDistance(tx_rx, n_rows, num_layers, neurons_per_layer, cut_data_set=1, test_size=0.3, batch_size=256, epochs=6):
    times = []
    distances = []
    relative_error = []

    x_train, y_train, x_test, y_test = getDataNormalizeAndSplit(tx_rx=tx_rx, cut_data_set=cut_data_set, test_size=test_size)

    # Create model
    model = FnnMode(input_shape=3, num_layers=num_layers, neurons_per_layer=neurons_per_layer, activation_function='relu')
    model.trainModel(x_train, y_train, batch_size=batch_size, epochs=epochs)
    loss, mae = model.getLossAndAccuracy()
    train_mae = mae [-1]

    random_indices = x_test.sample(n=n_rows).index

    random_x_test = x_test.loc[random_indices]
    random_y_test = y_test.loc[random_indices]

    for index, (random_x_index, random_y) in enumerate(zip(random_x_test.index, random_y_test), 1):
        random_x_values = x_test.iloc[[random_x_index]].values
        t, prediction = model.testTimePrediction(sample=random_x_values)

        params, label, prediction = deNormalizeData(random_x_values, random_y, prediction)

        # print(f"Parameters: {params}, Label: {label}, Prediction: {prediction}, Distance: {prediction-label}")
        times.append(t)
        distances.append(prediction[0][0]-label)
        relative_error.append(abs(prediction[0][0] - label) / abs(label) * 100)
        
    return distances, times, relative_error
    

def minimizeDataSet(tx_rx):
    global num_layers_, neurons_per_layer_

    # cut_data_set_list = [0.05, 0.01, 0.005, 0.001, 0.0005, 0.0001]
    cut_data_set_list = [0.05]
    batch_size = 256
    epochs = 6
    n_rows = 1000

    distances = []

    average_distances = []
    percentage_of_dataset = []

    for cut_data_set in cut_data_set_list:
        # Update values

        if cut_data_set < 0.05:
            batch_size = 32
            epochs = 10
        if cut_data_set < 0.005:
            batch_size = 8
            epochs = 15

        distances, times, relative_error = testSpeedAndDistance(tx_rx=tx_rx, cut_data_set=cut_data_set, num_layers=num_layers_, neurons_per_layer=neurons_per_layer_, n_rows=n_rows, batch_size=batch_size, epochs=epochs)

        average_distances.append(sum(distances)/len(distances))
        percentage_of_dataset.append(cut_data_set*100)

        n_bins = 100
        # ---------------- Absolute Error here ----------------
        plt.hist(distances, bins=n_bins, color='blue', edgecolor='black', range=(-0.5, 1))

        # Set ticks to go from -0.5 to 1
        x_ticks = np.arange(-0.5, 1.1, 0.1)
        plt.xticks(x_ticks)

        # Add labels and title
        plt.xlabel('Error [W]', fontsize=16)
        plt.ylabel('Number of Predictions', fontsize=16)
        plt.title(f'Histogram of Error committed between Prediction and Label for {cut_data_set*100}', fontsize=32)

        plt.get_current_fig_manager().window.state('zoomed')

        # Display the plot
        # plt.show(block=True)
        plt.savefig(f"absolute_error_histogram_{cut_data_set*100}%.png")

        print(f"For {cut_data_set*100} of the dataset, average error distance: {average_distances[-1]}")
        distances.clear()

        # ---------------- Relative error here ----------------
        plt.hist(relative_error, bins=n_bins, color='blue', edgecolor='black', range=(-0.1, 10))

        # Add labels and title
        plt.xlabel('Error [%]', fontsize=16)
        plt.ylabel('Number of Predictions', fontsize=16)
        plt.title(f'Histogram of Error committed between Prediction and Label for {cut_data_set*100}', fontsize=32)

        plt.get_current_fig_manager().window.state('zoomed')

        # Display the plot
        plt.show(block=True)
        plt.savefig(f"relative_error_histogram_{cut_data_set*100}%.png")

    print(average_distances)
    print(percentage_of_dataset)

def getDistanceFromPrediction(tx_rx):
    global num_layers_, neurons_per_layer_
    n_rows = 1000

    distances, times, relative_error = testSpeedAndDistance(tx_rx=tx_rx, num_layers=num_layers_, neurons_per_layer=neurons_per_layer_, n_rows=n_rows)

    n_bins = 100
    plt.hist(distances, bins=n_bins, color='blue', edgecolor='black', range=(-0.5, 1))

    # Optionally, you can set the x-ticks to ensure they are well-distributed
    x_ticks = np.arange(-0.5, 1.1, 0.1)
    plt.xticks(x_ticks)

    # Add labels and title
    plt.xlabel('Error [W]', fontsize=16)
    plt.ylabel('Number of Predictions', fontsize=16)
    plt.title('Histogram of Error committed between Prediction and Label', fontsize=32)

    # Display the plot
    plt.show(block=True)

    a = 0
    b = 0
    for dis in distances:
        if dis < 0.1 and dis > -0.1:
            b += 1
        if dis > 0.4:
            a +=1
    print(f"Numer of points beyond 0.4: {a}. Number of points inside +- 0.1 {b}")

def testSpeedPerformance(tx_rx):
    global num_layers_, neurons_per_layer_
    n_rows = 1000
    
    distances, times, relative_error = testSpeedAndDistance(tx_rx=tx_rx, num_layers=num_layers_, neurons_per_layer=neurons_per_layer_, n_rows=n_rows)

    print(f"Average time to perform a prediction: {sum(times)/len(times)} seconds")