import database.DbConnection as DbConnection
from datastructures.IotLogs import loadIotData
from datastructures.PsuLog import loadPsuData
from view.common import *
from datastructures.enums import Direction

def myMain():
    myDb = DbConnection.connectToDb()

    iot_logs = loadIotData(myDb=myDb, campaignId=170)
    if iot_logs == -1:
        return -1
        
    psu_logs = loadPsuData(myDb=myDb, campaignId=170)
    if psu_logs == -1:
        return -1

    found = iot_logs.searchPrach()
    if found == -1:
        return -1
    


    max = 0.0
    for psu_log in psu_logs:
        if float(psu_log.volts) > max:
            max = float(psu_log.volts)

    psuRawPlot(psu_logs=psu_logs)

if __name__ == "__main__":
    myMain()