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


def iotPostProcessing(myDb):
    sweeps = 1
    global Iot
    global campaign_iot_logs

    iot_rows = DbConnection.getDataFromDb(myDb=myDb, campaign_id=campaign_id, iot_psu=1)

    campaign_iot_logs.loadIotData(iot_rows, sweeps=sweeps)

    campaign_iot_logs.sortPhyLogEntries()
    campaign_iot_logs.sortNonPhyLogEntries()
    campaign_iot_logs.cleanData()

    if campaign_iot_logs.searchPrach() == -1:
        return -1
    campaign_iot_logs.updateTimeStamp()

    campaign_iot_logs.findHighestFrameAndSlot()
    campaign_iot_logs.getPsuMax()
    campaign_iot_logs.getMcs()
    campaign_iot_logs.getMimo()
    campaign_iot_logs.getFrequencyBand()
    # campaign_iot_logs.getAllNas()
    campaign_iot_logs.getRegistrationCompleteIndexTime()


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
    
    if Iot:
        threadIot = threading.Thread(target=iotPostProcessing, args=(myDb,))
        threadIot.start()
        
        Iot = False

    if Psu:
        threadPsu = threading.Thread(target=psuPostProcessing, args=(myDb,))
        threadPsu.start()

        Psu = False

    threadIot.join()
    threadPsu.join()

    while Psu == True and Iot == True:
        time.sleep(5)

    # psuRawPlot(psu_logs=campaign_psu_logs.campaign_psu_logs[1].psu_logs, y_min=-0.5, y_max=1, x_lim_min=campaign_iot_logs.campaign_iot_logs[1].importantIndexes.prach_time, x_lim_max=campaign_iot_logs.campaign_iot_logs[1].importantIndexes.registration_complete_time)
    psuRawPlot(psu_logs=campaign_psu_logs.campaign_psu_logs[1].psu_logs, y_min=-0.5, y_max=8)
    
    return 1

if __name__ == "__main__":
    myMain()