import database.DbConnection as DbConnection
from datastructures.IotLogs import IotLogs
from datastructures.PsuLog import PsuLogs
from datastructures.enums import Layer
from view.common import *

def myMain():
    myDb = DbConnection.connectToDb()
    iot_logs = IotLogs()
    psu_logs = PsuLogs()

    if iot_logs.loadIotData(myDb=myDb, campaignId=170) == -1:
        return -1
    
    foundPrach = iot_logs.searchPrach()
    if foundPrach == -1:
        return -1
    
    for iot_log in iot_logs.iot_logs:
        if iot_log.frame == -1 and iot_log.layer == Layer.PHY:
            print("Phy with -1")

    iot_logs.findHighestFrameAndSlot()
    iot_logs.sortPhyLogEntries()
    iot_logs.searchSib()
        

    #if psu_logs.loadPsuData(myDb=myDb, campaignId=170) == -1:
    #    return -1

    #foundVoltageSpike = psu_logs.searchVoltageSPike()
    #if foundVoltageSpike == -1:
    #    return -1

    #psu_logs.calculateTimePsuAndPower()


    psuRawPlot(psu_logs=psu_logs)

if __name__ == "__main__":
    myMain()