import os
import pickle
import numpy as np
import database.DbConnection as DbConnection
from DeepLearning.fnn import *
from datastructures.IotLogs import CampaignIotLogs
from datastructures.PsuLog import CampaignPsuLogs
from datastructures.enums import Layer
from view.common import *

campaign_id = 4

Iot = True
Psu = True

campaign_psu_logs = CampaignPsuLogs()
campaign_iot_logs = CampaignIotLogs()

load_from_DB_or_csv = False # True loads the data from the DB, False loads the data from a CSV

load_or_read_AllDataIot = False # True loads data from Pickle, False reads everything from the DB
load_or_read_AllDataPsu = False # True loads data from Pickle, False reads everything from the DB

saveToPickle = True


def psuPostProcessing(myDb):
    sweeps = None
    global Psu
    global campaign_psu_logs

    if load_from_DB_or_csv == True:
        psu_rows = DbConnection.getDataFromDb(myDb=myDb, campaign_id=campaign_id, iot_psu=0)
        campaign_psu_logs.loadData(psu_rows, sweeps=sweeps)
    elif load_from_DB_or_csv == False:
        campaign_psu_logs.loadDataFromCsv()
        time = [psu_log.origin for psu_log in campaign_psu_logs.campaign_psu_logs[0].psu_logs]
        amperes = [psu_log.amperes for psu_log in campaign_psu_logs.campaign_psu_logs[0].psu_logs]
        volts = [psu_log.volts for psu_log in campaign_psu_logs.campaign_psu_logs[0].psu_logs]
        # simplePlotTwoYValues(time, volts, amperes, "Time [s]", "Volts [V]", "Amperes [A]", "Voltage and Amperes registered")
        simplePlot(time, volts, "Time [s]", "Voltage [V]")
        simplePlot(time, amperes, "Time [s]", "Amperes [A]")
    
    if campaign_psu_logs.searchVoltageSpike() == -1:
        print("No voltage spike found")
        return -1
    
    campaign_psu_logs.calculateTimePsuAndPower()
    # campaign_psu_logs.findTwoMaxValues()

    if saveToPickle == True:
        with open(os.path.join('datastructures','files', 'ProcessedData', 'CampaignPsuLogs' + str(campaign_id) + '.pkl'), 'wb') as file:
            pickle.dump(campaign_psu_logs, file)

def iotPostProcessing(myDb):
    sweeps = None
    global Iot
    global campaign_iot_logs

    if load_from_DB_or_csv == True:
        iot_rows = DbConnection.getDataFromDb(myDb=myDb, campaign_id=campaign_id, iot_psu=1)
        campaign_iot_logs.loadIotData(iot_rows, sweeps=sweeps)
    elif load_from_DB_or_csv == False:
        campaign_iot_logs.loadDataFromCsv()

    
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

    campaign_iot_logs.getPuschTimes(lim=50)
    campaign_iot_logs.getPdcchTimes(lim=50)

    campaign_iot_logs.getAllPuschPowers(campaign_psu_logs)
    # campaign_iot_logs.getAllPdschPowers(campaign_psu_logs)
    campaign_iot_logs.getMeanAndDeviationPusch()
    # campaign_iot_logs.getMeanAndDeviationPdsch()

    if saveToPickle == True:
        with open(os.path.join('datastructures','files', 'ProcessedData', 'CampaignIotLogs' + str(campaign_id) + '.pkl'), 'wb') as file:
            pickle.dump(campaign_iot_logs, file)

    campaign_iot_logs.saveToCsv()
    campaign_iot_logs.printMcsAndPmax()

def myMain():
    myDb = DbConnection.connectToDb()
    global Iot
    global Psu
    global campaign_iot_logs
    global campaign_psu_logs
    global load_or_read_AllDataIot
    global load_or_read_AllDataPsu

        # ----------- PSU -----------
    if Psu == True:

        if load_or_read_AllDataPsu == False:
            psuPostProcessing(myDb=myDb)
        
        elif load_or_read_AllDataIot == True:
            with open(os.path.join('datastructures','files', 'ProcessedData', 'CampaignPsuLogs' + str(campaign_id) + '.pkl'), 'rb') as file:
                campaign_psu_logs = pickle.load(file)
    # ----------- PSU -----------

    # ----------- IOT -----------
    if Iot ==  True:

        if load_or_read_AllDataIot == False:
            iotPostProcessing(myDb=myDb)

        elif load_or_read_AllDataIot == True:
            with open(os.path.join('datastructures','files', 'ProcessedData', 'CampaignIotLogs' + str(campaign_id) + '.pkl'), 'rb') as file:
                campaign_iot_logs = pickle.load(file)
    # ----------- IOT -----------
    

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

    campaign_iot_logs.saveMeanAndDeviationToCsv(campaign_id)
    
    mean = []
    lower_ci = []
    upper_ci = []
    median = []
    mcs_indexes = []
    p_tx = []

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

        psuRawPlotWithLinesArray(psu_logs=campaign_psu_log.psu_logs, y_min=-0.5, y_max=4, lines_array=all_times, y_min_lim=campaign_iot_log.p_tx_min, y_max_lim=campaign_iot_log.p_tx_max)
        # psuRawPlotWithLinesArray(psu_logs=campaign_psu_log.psu_logs, y_min=-0.5, y_max=4, lines_array=all_times)
        mean.append(campaign_iot_log.p_tx_mean)
        lower_ci.append(campaign_iot_log.p_tx_confidence_interval[0])
        upper_ci.append(campaign_iot_log.p_tx_confidence_interval[1])
        median.append(campaign_iot_log.p_tx_median)
        mcs_indexes.append(campaign_iot_log.mcs_index)
        p_tx.append(campaign_iot_log.p_max)

    # simplePlot(mcs_indexes, mean, "MCS Index", "Power Consumption [W]", "Power Consumption based on MCS Index", scatter=1)
    # simplePlot(p_tx, mean, "Power Transmission [dBm]", "Power Consumption [W]", "Power based on Power Transmission", scatter=1)
    # plotConfidenceInterval(p_tx, mean, lower_ci=lower_ci, upper_ci=upper_ci)

    campaign_iot_logs.saveDataToCsvForDeepLearningModelPusch()

    return 1

if __name__ == "__main__":
    myMain()
    # firstSimpleModel()
    # evaluateBestModel()
    # minimizeDataSet()
