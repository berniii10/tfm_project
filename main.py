import database.DbConnection as DbConnection
from datastructures.IotLogs import IotLogs
from datastructures.PsuLog import PsuLogs
from view.common import *

def myMain():
    myDb = DbConnection.connectToDb()
    iot_logs = IotLogs()
    psu_logs = PsuLogs()

    if iot_logs.loadIotData(myDb=myDb, campaignId=170) == -1:
        return -1
        
    if psu_logs.loadPsuData(myDb=myDb, campaignId=170) == -1:
        return -1

    foundPrach = iot_logs.searchPrach()
    if foundPrach == -1:
        return -1
    
    foundVoltageSpike = psu_logs.searchVoltageSPike()
    if foundVoltageSpike == -1:
        return -1

    psu_logs.calculateTimePsuAndPower()
    iot_logs.findHighestFrameAndSlot()

    psuRawPlot(psu_logs=psu_logs)

if __name__ == "__main__":
    myMain()