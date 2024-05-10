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


def psuPostProcessing(myDb=None, pmax=None, mcs_table=None, mcs_index=None, n_antenna_ul=None, n_antenna_dl=None, tx_rx=None):
    sweeps = None
    global Psu
    global campaign_psu_logs

    if myDb != None:
        psu_rows = DbConnection.getDataFromDb(myDb=myDb, campaign_id=campaign_id, iot_psu=0)
        campaign_psu_logs.loadData(psu_rows, sweeps=sweeps)

    elif pmax != None and mcs_table != None and mcs_index != None and n_antenna_ul != None and n_antenna_dl != None:
        if campaign_psu_logs.loadDataFromCsv(pmax_list=pmax, mcs_table_list=mcs_table, mcs_index_list=mcs_index, n_antenna_ul_list=n_antenna_ul, n_antenna_dl_list=n_antenna_dl, tx_rx=tx_rx) == -1:
            return -1
    
    # time = [psu_log.origin for psu_log in campaign_psu_logs.campaign_psu_logs[0].psu_logs]
    # amperes = [psu_log.amperes for psu_log in campaign_psu_logs.campaign_psu_logs[0].psu_logs]
    # volts = [psu_log.volts for psu_log in campaign_psu_logs.campaign_psu_logs[0].psu_logs]
    # simplePlotTwoYValues(time, volts, amperes, "Time [s]", "Volts [V]", "Amperes [A]", "Voltage and Amperes registered")
    # simplePlot(time, volts, "Time [s]", "Voltage [V]")
    # simplePlot(time, amperes, "Time [s]", "Amperes [A]")

    if campaign_psu_logs.searchVoltageSpike() == -1:
        print("No voltage spike found")
        return -1
    
    campaign_psu_logs.calculateTimePsuAndPower()
    # campaign_psu_logs.findTwoMaxValues()

def iotPostProcessing(myDb=None, pmax=None, mcs_table=None, mcs_index=None, n_antenna_ul=None, n_antenna_dl=None, tx_rx=None):
    sweeps = None
    global Iot
    global campaign_iot_logs

    if myDb != None:
        iot_rows = DbConnection.getDataFromDb(myDb=myDb, campaign_id=campaign_id, iot_psu=1)
        campaign_iot_logs.loadIotData(iot_rows, sweeps=sweeps)

    elif pmax != None and mcs_table != None and mcs_index != None and n_antenna_ul != None and n_antenna_dl != None:
        if campaign_iot_logs.loadDataFromCsv(pmax_list=pmax, mcs_table_list=mcs_table, mcs_index_list=mcs_index, n_antenna_ul_list=n_antenna_ul, n_antenna_dl_list=n_antenna_dl, tx_rx=tx_rx) == -1:
            return -1

    campaign_iot_logs.sortPhyLogEntries()
    campaign_iot_logs.sortNonPhyLogEntries()
    campaign_iot_logs.cleanData()

    if campaign_iot_logs.searchPrach() == -1: # Update the index where the PRACH is found
        return -1
    campaign_iot_logs.updateTimeStamp()

    # campaign_iot_logs.findHighestFrameAndSlot()
    campaign_iot_logs.getPMax()
    # campaign_iot_logs.getMcs()
    # campaign_iot_logs.getMimo()
    campaign_iot_logs.getFrequencyBand()
    # campaign_iot_logs.getAllNas()
    campaign_iot_logs.getRegistrationCompleteIndexTime()

    campaign_iot_logs.getPuschTimes(lim=30)
    campaign_iot_logs.getPdcchTimes(lim=30)
    campaign_iot_logs.getPucchTimes(lim=30)
    campaign_iot_logs.getPdschTimes(lim=30)

    campaign_iot_logs.getAllPuschPowers(campaign_psu_logs)
    campaign_iot_logs.getAllPdschPowers(campaign_psu_logs)
    campaign_iot_logs.getMeanAndDeviationPusch()
    campaign_iot_logs.getMeanAndDeviationPdsch()

    campaign_iot_logs.printMcsAndPmax()

def commonLoad(tx_rx):
    global Iot
    global Psu
    global campaign_iot_logs
    global campaign_psu_logs
    

    if load_data_from == 'CSV':
        pmax = [21, 20, 19, 18, 17, 16, 15, 14, 13, 12, 11, 10, 9, 8, 7, 6, 5, 4, 3, 2, 1, 0, -1, -2, -3, -4, -5] # 21, 20, 19, 18, 17, 16, 15, 14, 13, 12, 11, 10, 9, 8, 7, 6, 5, 4, 3, 2, 1, 0, -1, -2, -3, -4, -5
        mcs_table = ['qam256'] # qam64
        mcs_index = [6, 7, 8, 9, 10] # 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17
        n_antenna_ul = [2]
        n_antenna_dl = [1]
        
        if Psu == True:
            if psuPostProcessing(pmax=pmax, mcs_table=mcs_table, mcs_index=mcs_index, n_antenna_ul=n_antenna_ul, n_antenna_dl=n_antenna_dl, tx_rx=tx_rx) == -1:
                return -1

        if Iot ==  True:
            if iotPostProcessing(pmax=pmax, mcs_table=mcs_table, mcs_index=mcs_index, n_antenna_ul=n_antenna_ul, n_antenna_dl=n_antenna_dl, tx_rx=tx_rx) == -1:
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

    if saveToPickle == True:
        with open(os.path.join('datastructures','files', 'ProcessedData', 'CampaignIotLogs' + str(campaign_id) + '.pkl'), 'wb') as file:
            pickle.dump(campaign_iot_logs, file)

def evaluatePmax(mcs=None):
    
    # Read the CSV file into a DataFrame
    df = pd.read_csv(os.path.join('DeepLearning', 'tx', 'prev', 'data' + '.csv'))

    # Specify the desired 'MCS' and 'MIMO' values
    if mcs == None:
        mcs_value = 10
    else:
        mcs_value = mcs
    mimo_value = 2

    # Filter the DataFrame based on the specified 'MCS' and 'MIMO' values
    filtered_df = df[(df['mcs'] == mcs_value) & (df['mimo'] == mimo_value)]

    # Group by 'pmax' and calculate the average label for each group
    average_labels = filtered_df.groupby('pmax')['label'].mean()

    mimo_value = 1
    # Filter the DataFrame based on the specified 'MCS' and 'MIMO' values
    filtered_df2 = df[(df['mcs'] == mcs_value) & (df['mimo'] == mimo_value)]

    # Group by 'pmax' and calculate the average label for each group
    average_labels2 = filtered_df2.groupby('pmax')['label'].mean()

    p_max = [21, 20, 19, 18, 17, 16, 15, 14, 13, 12, 11, 10, 9, 8, 7, 6, 5, 4, 3, 2, 1, 0, -1, -2, -3, -4, -5]

    simplePlot(p_max[::-1], average_labels, "Power Transmission [dBm]", "Power Consumption [W]", "Power Consumption based on Power Transmission for MIMO 2x2", scatter=1)
    simplePlotTwoYValues(p_max[::-1], average_labels, average_labels2, 'Transmission Power [dBm]', "Power Consumption [W]", 'MIMO 2x2', 'SISO', 'Power consumption based on Transmission Power for SISO and MIMO 2x2')
    simplePlot(p_max[::-1], average_labels2, "Power Transmission [dBm]", "Power Consumption [W]", "Power Consumption based on Power Transmission for SISO", scatter=1)

def evaluateMcs():
        # Read the CSV file into a DataFrame
    df = pd.read_csv(os.path.join('DeepLearning', 'tx', 'prev', 'data' + '.csv'))

    # Specify the desired 'MCS' and 'MIMO' values
    mimo_value = 1
    pmax = 21

    mcs_index1 = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17]
    mcs_index2 = [29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39]

    # Filter the DataFrame based on the specified 'MCS' and 'MIMO' values
    filtered_mcs64 = df[(df['pmax'] == pmax) & (df['mimo'] == mimo_value) & (df['mcs'].isin(mcs_index1))]
    filtered_mcs256 = df[(df['pmax'] == pmax) & (df['mimo'] == mimo_value) & (df['mcs'].isin(mcs_index2))]

    # Group by 'pmax' and calculate the average label for each group
    average_labels_filtered_mcs64 = filtered_mcs64.groupby('mcs')['label'].mean()
    average_labels_filtered_mcs256 = filtered_mcs256.groupby('mcs')['label'].mean()

    simplePlot(mcs_index1, average_labels_filtered_mcs64, "MCS Index", "Power Consumption [W]", "Power Consumption based on MCS Index for table 64QAM", scatter=1)
    simplePlot(mcs_index1[:10], average_labels_filtered_mcs256, "MCS Index", "Power Consumption [W]", "Power Consumption based on MCS Index for table 256QAM", scatter=1)

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

    file = ''

    if tx_rx == 'tx':
        file = 'outputTx.txt'
    elif tx_rx == 'rx':
        file = 'outputRx.txt'
    
    with open(file, "a") as file:
        for campaign_psu_log, campaign_iot_log in zip(campaign_psu_logs.campaign_psu_logs, campaign_iot_logs.campaign_iot_logs):

            #print(f"For power transmission: {campaign_iot_log.p_max}dBm, MCS Index: {campaign_iot_log.mcs_index} and Table: {campaign_iot_log.mcs_table}, MIMO: {campaign_iot_log.mimo} and BW: {campaign_iot_log.bw} and Frequency Band {campaign_iot_log.freq_band}\n"
            #    f"- Mean of the Power Consumption was {campaign_iot_log.p_tx_mean:.3f} [W]\n"
            #    f"- Median of the Power Consumption was {campaign_iot_log.p_tx_median:.3f} [W]\n"
            #    f"- Minimum of the Power Consumption was {campaign_iot_log.p_tx_min:.3f} [W]\n"
            #    f"- Maximum of the Power Consumption was {campaign_iot_log.p_tx_max:.3f} [W]\n"
            #    f"- Standard Deviation {campaign_iot_log.p_tx_standard_deviation:.3f} or {campaign_iot_log.p_tx_standard_deviation*100/campaign_iot_log.p_tx_mean:.3f}%\n"
            #    f"- Confidence Interval Low {campaign_iot_log.p_tx_confidence_interval[0]:.3f}\n"
            #    f"- Confidence Interval High {campaign_iot_log.p_tx_confidence_interval[1]:.3f}\n"
            #    "--------------------------------------------------------------------")

            print(rf"\textbf{campaign_iot_log.p_max}  & {campaign_iot_log.p_tx_mean:.3f}  & {campaign_iot_log.p_tx_median:.3f}  & {campaign_iot_log.p_tx_standard_deviation:.3f}  & {campaign_iot_log.p_tx_confidence_interval[0]:.3f}  & {campaign_iot_log.p_tx_confidence_interval[1]:.3f} \\ \hline")
            
            #file.write(f"For power transmission: {campaign_iot_log.p_max}dBm, MCS Index: {campaign_iot_log.mcs_index} and Table: {campaign_iot_log.mcs_table}, MIMO: {campaign_iot_log.mimo} and BW: {campaign_iot_log.bw} and Frequency Band {campaign_iot_log.freq_band}\n"
            #f"- Mean of the Power Consumption was {campaign_iot_log.p_tx_mean:.3f} [W]\n"
            #f"- Median of the Power Consumption was {campaign_iot_log.p_tx_median:.3f} [W]\n"
            #f"- Minimum of the Power Consumption was {campaign_iot_log.p_tx_min:.3f} [W]\n"
            #f"- Maximum of the Power Consumption was {campaign_iot_log.p_tx_max:.3f} [W]\n"
            #f"- Standard Deviation {campaign_iot_log.p_tx_standard_deviation:.3f} or {campaign_iot_log.p_tx_standard_deviation*100/campaign_iot_log.p_tx_mean:.3f}%\n"
            #f"- Confidence Interval Low {campaign_iot_log.p_tx_confidence_interval[0]:.3f}\n"
            #f"- Confidence Interval High {campaign_iot_log.p_tx_confidence_interval[1]:.3f}\n"
            #"--------------------------------------------------------------------")

            all_times = campaign_iot_log.importantIndexes.getAllTimesList()
            # psuRawPlotWithLinesArray(psu_logs=campaign_psu_log.psu_logs, y_min=-0.5, y_max=4, lines_array=all_times, y_min_lim=campaign_iot_log.p_tx_min, y_max_lim=campaign_iot_log.p_tx_max)
            # psuRawPlotWithLinesArray(psu_logs=campaign_psu_log.psu_logs, y_min=-0.5, y_max=4, lines_array=all_times)

            mean.append(campaign_iot_log.p_tx_mean)
            lower_ci.append(campaign_iot_log.p_tx_confidence_interval[0])
            upper_ci.append(campaign_iot_log.p_tx_confidence_interval[1])
            median.append(campaign_iot_log.p_tx_median)
            mcs_indexes.append(campaign_iot_log.mcs_index)
            p_tx.append(campaign_iot_log.p_max)

            # psuRawPlotWithLinesArray(psu_logs=campaign_psu_log.psu_logs, y_min=-0.5, y_max=4, lines_array=all_times, y_min_lim=campaign_iot_log.p_tx_min, y_max_lim=campaign_iot_log.p_tx_max)
        
        all_times = campaign_iot_logs.campaign_iot_logs[0].importantIndexes.getAllTimesList()
        # psuRawPlotWithLinesArray(psu_logs=campaign_psu_logs.campaign_psu_logs[0].psu_logs, y_min=-0.5, y_max=4, lines_array=all_times, y_min_lim=campaign_iot_log.p_tx_min, y_max_lim=campaign_iot_log.p_tx_max)

    # simplePlot(mcs_indexes, mean, "MCS Index", "Power Consumption [W]", "Power Consumption based on MCS Index", scatter=1)
    # simplePlot(p_tx, mean, "Power Transmission [dBm]", "Power Consumption [W]", "Power based on Power Transmission", scatter=1)
    # plotConfidenceInterval(p_tx, mean, lower_ci=lower_ci, upper_ci=upper_ci)

    if tx_rx == 'tx':
        campaign_iot_logs.saveDataToCsvForDeepLearningModelPusch()
        pass
    elif tx_rx == 'rx':
        campaign_iot_logs.saveDataToCsvForDeepLearningModelPdsch()
        pass

    return 1

if __name__ == "__main__":
    tx_rx = 'tx'

    # evaluateMcs()
    # evaluatePmax()

    # commonLoad(tx_rx)
    # myMain(tx_rx=tx_rx)
    
    # Deep Learning Here

    # firstSimpleModel()
    # evaluateBestModel()
    minimizeDataSet()
    # testSpeedPerformance()
