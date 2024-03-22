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
Psu = False

campaign_psu_logs = CampaignPsuLogs()
campaign_iot_logs = CampaignIotLogs()

load_or_read_AllDataIot = False # True loads data from Pickle, False reads everything from the DB
load_or_read_AllDataPsu = False # True loads data from Pickle, False reads everything from the DB

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
    global Psu
    global campaign_psu_logs

    psu_rows = DbConnection.getDataFromDb(myDb=myDb, campaign_id=campaign_id, iot_psu=0)
    campaign_psu_logs.loadData(psu_rows)
    
    if campaign_psu_logs.searchVoltageSpike() == -1:
        return -1
    
    campaign_psu_logs.calculateTimePsuAndPower()
    # campaign_psu_logs.findTwoMaxValues()

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
            
            Iot = False

        elif load_or_read_AllDataIot == True:
            with open(os.path.join('datastructures','files', 'CampaignIotLogs' + str(campaign_id) + '.pkl'), 'rb') as file:
                campaign_iot_logs = pickle.load(file)
    # ----------- IOT -----------


    # ----------- PSU -----------
    if Psu == True:

        if load_or_read_AllDataPsu == False:
            threadPsu = threading.Thread(target=psuPostProcessing, args=(myDb,))
            threadPsu.start()

            Psu = False
        
        elif load_or_read_AllDataIot == True:
            pass    # Load data here

        threadPsu.join()
        psuRawPlot(psu_logs=campaign_psu_logs.campaign_psu_logs[0].psu_logs, y_min=-0.5, y_max=8)
    # ----------- PSU -----------
        
    threadIot.join()
    
    while Psu == True and Iot == True:
        time.sleep(10)
    
    psuRawPlot(psu_logs=campaign_psu_logs.campaign_psu_logs[0].psu_logs, y_min=-0.5, y_max=8, x_lim_min=campaign_iot_logs.campaign_iot_logs[0].importantIndexes.prach_time, x_lim_max=campaign_iot_logs.campaign_iot_logs[0].importantIndexes.registration_complete_time)
    
    return 1

if __name__ == "__main__":
    myMain()