import os
import pickle
import database.DbConnection as DbConnection
from datastructures.IotLogs import CampaignIotLogs
from datastructures.PsuLog import CampaignPsuLogs
from datastructures.enums import Layer
from view.common import *
import threading
import time

campaign_id = 376 # 221

Iot = True
Psu = True

campaign_psu_logs = CampaignPsuLogs()
campaign_iot_logs = CampaignIotLogs()

load_or_read_AllDataIot = True # True loads data from Pickle, False reads everything from the DB
load_or_read_AllDataPsu = True # True loads data from Pickle, False reads everything from the DB

saveToPickle = False


def iotPostProcessing(myDb):
    sweeps = 1
    global Iot
    global campaign_iot_logs

    iot_rows = DbConnection.getDataFromDb(myDb=myDb, campaign_id=campaign_id, iot_psu=1)

    campaign_iot_logs.loadIotData(iot_rows, sweeps=sweeps)
    #if campaign_iot_logs.searchPrach() == -1: # Check if PRACH exists before processing the data.
    #    return -1

    campaign_iot_logs.sortPhyLogEntries()
    campaign_iot_logs.sortNonPhyLogEntries()
    campaign_iot_logs.cleanData()

    if campaign_iot_logs.searchPrach() == -1: # Update the index where the PRACH is found
        return -1
    campaign_iot_logs.updateTimeStamp()

    # campaign_iot_logs.findHighestFrameAndSlot()
    campaign_iot_logs.getPsuMax()
    campaign_iot_logs.getMcs()
    campaign_iot_logs.getMimo()
    campaign_iot_logs.getFrequencyBand()
    # campaign_iot_logs.getAllNas()
    campaign_iot_logs.getRegistrationCompleteIndexTime()

    if saveToPickle == True:
        with open(os.path.join('datastructures','files', 'CampaignIotLogs' + str(campaign_id) + '.pkl'), 'wb') as file:
            pickle.dump(campaign_iot_logs, file)

    campaign_iot_logs.saveToCsv()


def psuPostProcessing(myDb):
    sweeps = 1
    global Psu
    global campaign_psu_logs

    psu_rows = DbConnection.getDataFromDb(myDb=myDb, campaign_id=campaign_id, iot_psu=0)
    campaign_psu_logs.loadData(psu_rows, sweeps=sweeps)
    
    if campaign_psu_logs.searchVoltageSpike() == -1:
        return -1
    
    campaign_psu_logs.calculateTimePsuAndPower()
    # campaign_psu_logs.findTwoMaxValues()

    if saveToPickle == True:
        with open(os.path.join('datastructures','files', 'CampaignPsuLogs' + str(campaign_id) + '.pkl'), 'wb') as file:
            pickle.dump(campaign_psu_logs, file)

def myMain():
    myDb = DbConnection.connectToDb()
    global Iot
    global Psu
    global campaign_iot_logs
    global campaign_psu_logs
    global load_or_read_AllDataIot
    global load_or_read_AllDataPsu

    # ----------- IOT -----------
    if Iot ==  True:

        if load_or_read_AllDataIot == False:
            threadIot = threading.Thread(target=iotPostProcessing, args=(myDb,))
            threadIot.start()

        elif load_or_read_AllDataIot == True:
            with open(os.path.join('datastructures','files', 'CampaignIotLogs' + str(campaign_id) + '.pkl'), 'rb') as file:
                campaign_iot_logs = pickle.load(file)
            
        Iot = False
    # ----------- IOT -----------


    # ----------- PSU -----------
    if Psu == True:

        if load_or_read_AllDataPsu == False:
            threadPsu = threading.Thread(target=psuPostProcessing, args=(myDb,))
            threadPsu.start()
        
        elif load_or_read_AllDataIot == True:
            with open(os.path.join('datastructures','files', 'CampaignPsuLogs' + str(campaign_id) + '.pkl'), 'rb') as file:
                campaign_psu_logs = pickle.load(file)

        if load_or_read_AllDataPsu == False:
            threadPsu.join()

        Psu = False
        # psuRawPlot(psu_logs=campaign_psu_logs.campaign_psu_logs[0].psu_logs, y_min=-0.5, y_max=8)
    # ----------- PSU -----------
    
    if load_or_read_AllDataIot == False:
        threadIot.join()
    
    while Psu == True and Iot == True:
        time.sleep(10)

    # psuRawPlot(psu_logs=campaign_psu_logs.campaign_psu_logs[0].psu_logs, y_min=-0.5, y_max=4, x_lim_min=campaign_iot_logs.campaign_iot_logs[0].importantIndexes.prach_time, x_lim_max=campaign_iot_logs.campaign_iot_logs[0].importantIndexes.registration_complete_time)

    # DATA is ready here for proper post processing
    

    campaign_iot_logs.getPuschTimes()
    campaign_iot_logs.getPdcchTimes()

    all_times = campaign_iot_logs.campaign_iot_logs[0].importantIndexes.getAllTimesList()
    all_times.append(campaign_iot_logs.getPdschTimes())
    all_times.append(campaign_iot_logs.getPucchTimes())
    all_times.append([campaign_iot_logs.campaign_iot_logs[0].importantIndexes.prach_time])
    all_times.append([campaign_iot_logs.campaign_iot_logs[0].importantIndexes.registration_complete_time])

    psuRawPlotWithLinesArray(psu_logs=campaign_psu_logs.campaign_psu_logs[0].psu_logs, y_min=-0.25, y_max=2, lines_array=all_times)

    
    
    return 1

if __name__ == "__main__":
    myMain()