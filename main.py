import os, glob
import pickle
import itertools
import numpy as np
import database.DbConnection as DbConnection
from DeepLearning.fnn import *
from datastructures.IotLogs import CampaignIotLogs
from datastructures.PsuLog import CampaignPsuLogs
from datastructures.enums import Layer
from view.common import *

campaign_id = 0

Iot = True
Psu = True

campaign_psu_logs = CampaignPsuLogs()
campaign_iot_logs = CampaignIotLogs()

load_data_from = 'CSV'  # Possible sources: CSV, Pickle, DB
                        # CSV loads from CSV file
                        # Pickle loads from Pickle File
                        # DB loads from DB

saveToPickle = False


def psuPostProcessing(myDb=None, pmax=None, mcs_table=None, mcs_index=None, n_antenna_ul=None, n_antenna_dl=None):
    sweeps = None
    global Psu
    global campaign_psu_logs

    if myDb != None:
        psu_rows = DbConnection.getDataFromDb(myDb=myDb, campaign_id=campaign_id, iot_psu=0)
        campaign_psu_logs.loadData(psu_rows, sweeps=sweeps)

    elif pmax != None and mcs_table != None and mcs_index != None and n_antenna_ul != None and n_antenna_dl != None:
        campaign_psu_logs.loadDataFromCsv(pmax_list=pmax, mcs_table_list=mcs_table, mcs_index_list=mcs_index, n_antenna_ul_list=n_antenna_ul, n_antenna_dl_list=n_antenna_dl)
    
    time = [psu_log.origin for psu_log in campaign_psu_logs.campaign_psu_logs[0].psu_logs]
    amperes = [psu_log.amperes for psu_log in campaign_psu_logs.campaign_psu_logs[0].psu_logs]
    volts = [psu_log.volts for psu_log in campaign_psu_logs.campaign_psu_logs[0].psu_logs]
    # simplePlotTwoYValues(time, volts, amperes, "Time [s]", "Volts [V]", "Amperes [A]", "Voltage and Amperes registered")
    # simplePlot(time, volts, "Time [s]", "Voltage [V]")
    # simplePlot(time, amperes, "Time [s]", "Amperes [A]")

    if campaign_psu_logs.searchVoltageSpike() == -1:
        print("No voltage spike found")
        return -1
    
    campaign_psu_logs.calculateTimePsuAndPower()
    # campaign_psu_logs.findTwoMaxValues()

def iotPostProcessing(myDb=None, pmax=None, mcs_table=None, mcs_index=None, n_antenna_ul=None, n_antenna_dl=None):
    sweeps = None
    global Iot
    global campaign_iot_logs

    if myDb != None:
        iot_rows = DbConnection.getDataFromDb(myDb=myDb, campaign_id=campaign_id, iot_psu=1)
        campaign_iot_logs.loadIotData(iot_rows, sweeps=sweeps)

    elif pmax != None and mcs_table != None and mcs_index != None and n_antenna_ul != None and n_antenna_dl != None:
        campaign_iot_logs.loadDataFromCsv(pmax_list=pmax, mcs_table_list=mcs_table, mcs_index_list=mcs_index, n_antenna_ul_list=n_antenna_ul, n_antenna_dl_list=n_antenna_dl)

    
    #if campaign_iot_logs.searchPrach() == -1: # Check if PRACH exists before processing the data.
    #    return -1

    campaign_iot_logs.sortPhyLogEntries()
    campaign_iot_logs.sortNonPhyLogEntries()
    campaign_iot_logs.cleanData()

    if campaign_iot_logs.searchPrach() == -1: # Update the index where the PRACH is found
        return -1
    campaign_iot_logs.updateTimeStamp()

    # campaign_iot_logs.findHighestFrameAndSlot()
    campaign_iot_logs.getPMax()
    campaign_iot_logs.getMcs()
    campaign_iot_logs.getMimo()
    campaign_iot_logs.getFrequencyBand()
    # campaign_iot_logs.getAllNas()
    campaign_iot_logs.getRegistrationCompleteIndexTime()

    campaign_iot_logs.getPuschTimes(lim=30)
    campaign_iot_logs.getPdcchTimes(lim=30)
    # campaign_iot_logs.getPucchTimes(lim=30)

    campaign_iot_logs.getAllPuschPowers(campaign_psu_logs)
    # campaign_iot_logs.getAllPdschPowers(campaign_psu_logs)
    campaign_iot_logs.getMeanAndDeviationPusch()
    # campaign_iot_logs.getMeanAndDeviationPdsch()

    # campaign_iot_logs.saveToCsv()
    campaign_iot_logs.printMcsAndPmax()

def commonLoad():
    global Iot
    global Psu
    global campaign_iot_logs
    global campaign_psu_logs
    global load_data_from5
    

    if load_data_from == 'CSV':
        pmax = [21, 20, 19, 18, 17, 16, 15, 14, 13, 12, 11, 10, 9, 8, 7, 6, 5, 4, 3, 2, 1, 0, -1, -2, -3, -4, -5] # 21, 20, 19, 18, 17, 16, 15, 14, 13, 12, 11, 10, 9, 8, 7, 6, 5, 4, 3, 2, 1, 0, -1, -2, -3, -4, -5
        mcs_table = ['qam64'] # qam64
        mcs_index = [0] # 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18
        n_antenna_ul = [2]
        n_antenna_dl = [2]
        
        if Psu == True:
            if psuPostProcessing(pmax=pmax, mcs_table=mcs_table, mcs_index=mcs_index, n_antenna_ul=n_antenna_ul, n_antenna_dl=n_antenna_dl) == -1:
                return -1

        if Iot ==  True:
            if iotPostProcessing(pmax=pmax, mcs_table=mcs_table, mcs_index=mcs_index, n_antenna_ul=n_antenna_ul, n_antenna_dl=n_antenna_dl) == -1:
                return -1

        if saveToPickle == True:
            with open(os.path.join('datastructures','files', 'ProcessedData', 'PsuLogs-' + 'pmax' + str(pmax[0]) + '_' + str(pmax[-1]) + "-" + "-".join(mcs_table) + str(mcs_index[0]) + '_' + str(mcs_index[-1]) + '-' + 'UL' + str(n_antenna_ul[0]) + 'DL' + str(n_antenna_dl[0]) + '.pkl'), 'wb') as file:
                pickle.dump(campaign_psu_logs, file)
                
            with open(os.path.join('datastructures','files', 'ProcessedData', 'IotLogs-' + 'pmax' + str(pmax[0]) + '_' + str(pmax[-1]) + "-" + "-".join(mcs_table) + str(mcs_index[0]) + '_' + str(mcs_index[-1]) + '-' + 'UL' + str(n_antenna_ul[0]) + 'DL' + str(n_antenna_dl[0]) + '.pkl'), 'wb') as file:
                pickle.dump(campaign_iot_logs, file)

    elif load_data_from == 'Pickle':
        if Psu == True:
            with open(os.path.join('datastructures','files', 'ProcessedData', 'CampaignPsuLogs' + str(campaign_id) + '.pkl'), 'rb') as file:
                campaign_psu_logs = pickle.load(file)

        if Iot ==  True:
            with open(os.path.join('datastructures','files', 'ProcessedData', 'CampaignIotLogs' + str(campaign_id) + '.pkl'), 'rb') as file:
                campaign_iot_logs = pickle.load(file)

    elif load_data_from == 'DB':
        myDb = DbConnection.connectToDb()
        if Psu == True:
            psuPostProcessing(myDb=myDb)

        if Iot ==  True:
            iotPostProcessing(myDb=myDb)  

        if saveToPickle == True:
            with open(os.path.join('datastructures','files', 'ProcessedData', 'CampaignIotLogs' + str(campaign_id) + '.pkl'), 'rb') as file:
                campaign_iot_logs = pickle.dump(file)  

            with open(os.path.join('datastructures','files', 'ProcessedData', 'CampaignPsuLogs' + str(campaign_id) + '.pkl'), 'rb') as file:
                campaign_iot_logs = pickle.dump(file)       

    # psuRawPlot(psu_logs=campaign_psu_logs.campaign_psu_logs[0].psu_logs, y_min=-0.5, y_max=4, x_lim_min=campaign_iot_logs.campaign_iot_logs[0].importantIndexes.prach_time, x_lim_max=campaign_iot_logs.campaign_iot_logs[0].importantIndexes.registration_complete_time)

    # DATA is ready here for proper post processing
    
    # for i, campaign_psu_log in enumerate(campaign_psu_logs.campaign_psu_logs):
        # psuRawPlotVA(campaign_psu_log.psu_logs, -0.5, 4, title=f"P_max = {campaign_iot_logs.campaign_iot_logs[i].p_max}")
        # psuRawPlot(campaign_psu_log.psu_logs, -5, 10, title=f"P_max = {campaign_iot_logs.campaign_iot_logs[i].p_max}")

    if saveToPickle == True:
        with open(os.path.join('datastructures','files', 'ProcessedData', 'CampaignIotLogs' + str(campaign_id) + '.pkl'), 'wb') as file:
            pickle.dump(campaign_iot_logs, file)
    
    # getPsuAssociatedWithResultTypeId(1365)

    if saveToPickle == True:
        with open(os.path.join('datastructures','files', 'ProcessedData', 'CampaignIotLogs' + str(campaign_id) + '.pkl'), 'wb') as file:
            pickle.dump(campaign_iot_logs, file)

def evaluatePmax():
    global campaign_iot_logs
    global campaign_psu_logs

    p_max_mean = []
    p_max = []

    for campaign_iot_log in campaign_iot_logs.campaign_iot_logs:
        p_max_mean.append(campaign_iot_log.p_tx_mean)
        p_max.append(campaign_iot_log.p_max)

    simplePlot(p_max, p_max_mean, "Power Transmission", "Power Consumption", "Power Consumption based on Power Transmission")

def createHeatMap():
    global campaign_iot_logs
    global campaign_psu_logs

    data = [[]]
    for campaign_iot_log in campaign_iot_logs.campaign_iot_logs:
        print(f"Pmax: {campaign_iot_log.p_max}, MCS Table: {campaign_iot_log.mcs_table}, MCS Index: {campaign_iot_log.mcs_index}, MIMO: {campaign_iot_log.mimo}, Mean Transmission Power{campaign_iot_log.p_tx_mean}")

    # Create a heatmap using imshow
    plt.imshow(data, cmap='hot', interpolation='nearest')

    # Add a colorbar to the heatmap
    plt.colorbar()

    # Display the heatmap
    plt.show()

def myMain(tx_rx):
    global campaign_iot_logs
    global campaign_psu_logs

    campaign_iot_logs.saveMeanAndDeviationToCsv(campaign_id)
    
    mean = []
    lower_ci = []
    upper_ci = []
    median = []
    mcs_indexes = []
    p_tx = []
    with open("outputData.txt", "a") as file:
        for campaign_psu_log, campaign_iot_log in zip(campaign_psu_logs.campaign_psu_logs, campaign_iot_logs.campaign_iot_logs):
            all_times = campaign_iot_log.importantIndexes.getAllTimesList()
            #all_times.append(campaign_iot_log.getPdschTimes())
            #all_times.append(campaign_iot_log.getPucchTimes())

            print(f"For power transmission: {campaign_iot_log.p_max}dBm, MCS Index: {campaign_iot_log.mcs_index} and Table: {campaign_iot_log.mcs_table}, MIMO: {campaign_iot_log.mimo} and BW: {campaign_iot_log.bw} and Frequency Band {campaign_iot_log.freq_band}\n"
                f"- Mean of the Power Consumption was {campaign_iot_log.p_tx_mean:.3f} [W]\n"
                f"- Median of the Power Consumption was {campaign_iot_log.p_tx_median:.3f} [W]\n"
                f"- Minimum of the Power Consumption was {campaign_iot_log.p_tx_min:.3f} [W]\n"
                f"- Maximum of the Power Consumption was {campaign_iot_log.p_tx_max:.3f} [W]\n"
                f"- Standard Deviation {campaign_iot_log.p_tx_standard_deviation:.3f} or {campaign_iot_log.p_tx_standard_deviation*100/campaign_iot_log.p_tx_mean:.3f}%\n"
                f"- Confidence Interval Low {campaign_iot_log.p_tx_confidence_interval[0]:.3f}\n"
                f"- Confidence Interval High {campaign_iot_log.p_tx_confidence_interval[1]:.3f}\n"
                "--------------------------------------------------------------------")

            
            #file.write(f"For power transmission: {campaign_iot_log.p_max}dBm, MCS Index: {campaign_iot_log.mcs_index} and Table: {campaign_iot_log.mcs_table}, MIMO: {campaign_iot_log.mimo} and BW: {campaign_iot_log.bw} and Frequency Band {campaign_iot_log.freq_band}\n"
            #f"- Mean of the Power Consumption was {campaign_iot_log.p_tx_mean:.3f} [W]\n"
            #f"- Median of the Power Consumption was {campaign_iot_log.p_tx_median:.3f} [W]\n"
            #f"- Minimum of the Power Consumption was {campaign_iot_log.p_tx_min:.3f} [W]\n"
            #f"- Maximum of the Power Consumption was {campaign_iot_log.p_tx_max:.3f} [W]\n"
            #f"- Standard Deviation {campaign_iot_log.p_tx_standard_deviation:.3f} or {campaign_iot_log.p_tx_standard_deviation*100/campaign_iot_log.p_tx_mean:.3f}%\n"
            #f"- Confidence Interval Low {campaign_iot_log.p_tx_confidence_interval[0]:.3f}\n"
            #f"- Confidence Interval High {campaign_iot_log.p_tx_confidence_interval[1]:.3f}\n"
            #"--------------------------------------------------------------------")

            # psuRawPlotWithLinesArray(psu_logs=campaign_psu_log.psu_logs, y_min=-0.5, y_max=4, lines_array=all_times, y_min_lim=campaign_iot_log.p_tx_min, y_max_lim=campaign_iot_log.p_tx_max)
            # psuRawPlotWithLinesArray(psu_logs=campaign_psu_log.psu_logs, y_min=-0.5, y_max=4, lines_array=all_times)
            mean.append(campaign_iot_log.p_tx_mean)
            lower_ci.append(campaign_iot_log.p_tx_confidence_interval[0])
            upper_ci.append(campaign_iot_log.p_tx_confidence_interval[1])
            median.append(campaign_iot_log.p_tx_median)
            mcs_indexes.append(campaign_iot_log.mcs_index)
            p_tx.append(campaign_iot_log.p_max)

            psuRawPlotWithLinesArray(psu_logs=campaign_psu_log.psu_logs, y_min=-0.5, y_max=4, lines_array=all_times, y_min_lim=campaign_iot_log.p_tx_min, y_max_lim=campaign_iot_log.p_tx_max)

        psuRawPlotWithLinesArray(psu_logs=campaign_psu_logs.campaign_psu_logs[0].psu_logs, y_min=-0.5, y_max=4, lines_array=all_times, y_min_lim=campaign_iot_log.p_tx_min, y_max_lim=campaign_iot_log.p_tx_max)

    # simplePlot(mcs_indexes, mean, "MCS Index", "Power Consumption [W]", "Power Consumption based on MCS Index", scatter=1)
    # simplePlot(p_tx, mean, "Power Transmission [dBm]", "Power Consumption [W]", "Power based on Power Transmission", scatter=1)
    # plotConfidenceInterval(p_tx, mean, lower_ci=lower_ci, upper_ci=upper_ci)

    if tx_rx == 'tx':
        pass
        # campaign_iot_logs.saveDataToCsvForDeepLearningModelPusch()
    elif tx_rx == 'rx':
        pass

    return 1

def checkFiles():
        
    # Specify the directory path
    directory_path = os.path.join('datastructures','files', 'CampaignOutput')
    # Define the ranges for N, X, Y, and p
    N_values = list(range(21, -6, -1))
    X_values = ['qam64', 'qam256']
    Y_values = {'qam64': list(range(18)), 'qam256': list(range(11))}
    p_values = [1, 2]

    # Generate all possible combinations
    all_combinations = list(itertools.product(N_values, X_values, p_values))
    all_combinations = [(N, X, Y) for N, X, p in all_combinations for Y in Y_values[X]]


    # Get a list of all files in the directory
    existing_files = os.listdir(directory_path)

    # Create a list to store missing combinations
    missing_combinations = []

    # Check for missing combinations
    for combination in all_combinations:
        filename = f"*pmax{combination[0]}_MCS{combination[1]}-{combination[2]}_UL{combination[2]}_DL{combination[2]}*"
        if not any(filename in file for file in existing_files):
            missing_combinations.append(combination)

    # Print or save the missing combinations
    with open("missing_combinations.txt", "w") as file:
        for combination in missing_combinations:
            file.write(f"{combination}\n")

def checkMissingCombiantions():
    # Define the ranges for each column
    pmax_range = range(-5, 22)  # Exclude 22
    mimo_range = range(1, 3)    # Exclude 3
    mcs_range = list(range(0, 18)) + list(range(29, 40))  # Exclude 18 and 40

    # Generate all possible combinations within the specified ranges
    all_combinations = list(itertools.product(pmax_range, mimo_range, mcs_range))

    # Read the CSV file
    df = pd.read_csv(os.path.join('DeepLearning','tx', 'data' + '.csv'))

    # Extract unique combinations from the dataframe
    unique_combinations = set(zip(df['pmax'], df['mimo'], df['mcs']))

    # Find the missing combinations
    missing_combinations = [comb for comb in all_combinations if comb not in unique_combinations]

    # Print or save the missing combinations
    with open("missing_combinations.txt", "w") as file:
        for combination in missing_combinations:
            file.write(f"{combination}\n")

if __name__ == "__main__":
    tx_rx = 'tx'

    with open("outputData.txt", "a") as file:
        # Read the CSV file into a DataFrame
        df = pd.read_csv(os.path.join('DeepLearning','tx', 'mimo2', 'data' + '.csv'))

        # Group by 'pmax', 'mcs', and 'mimo', and calculate the average label for each group
        result = df.groupby(['pmax', 'mcs', 'mimo'])['label'].mean()

        # Output the results
        file.write(result)

    # checkFiles()
    # checkMissingCombiantions()
    commonLoad()

    evaluatePmax()
    myMain(tx_rx=tx_rx)

    # firstSimpleModel()
    # evaluateBestModel()
    # minimizeDataSet()
    # testSpeedPerformance()
