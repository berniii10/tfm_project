import database.DbConnection as DbConnection
from datastructures.IotLogs import CampaignIotLogs
from datastructures.PsuLog import CampaignPsuLogs
from datastructures.enums import Layer
from view.common import *

campaign_id = 221

def myMain():
    myDb = DbConnection.connectToDb()

    #IoT
    iot_rows = DbConnection.getDataFromDb(myDb=myDb, campaign_id=campaign_id, iot_psu=1)

    campaign_iot_logs = CampaignIotLogs()
    campaign_iot_logs.loadIotData(iot_rows)

    campaign_iot_logs.sortPhyLogEntries()
    campaign_iot_logs.sortNonPhyLogEntries()
    campaign_iot_logs.cleanData()

    # print("Testplans in the campaign: ",campaign_iot_logs.howManyTestplans())
    if campaign_iot_logs.searchPrach() == -1:
        return -1
    
    campaign_iot_logs.updateTimeStamp()
    campaign_iot_logs.searchPrach()
    campaign_iot_logs.findHighestFrameAndSlot()
    campaign_iot_logs.getPsuMax()
    campaign_iot_logs.getMcs()
    campaign_iot_logs.getMimo()
    campaign_iot_logs.getFrequencyBand()
    # campaign_iot_logs.getAllNas()


    # PSU
    psu_rows = DbConnection.getDataFromDb(myDb=myDb, campaign_id=campaign_id, iot_psu=0)
    campaign_psu_logs = CampaignPsuLogs()
    campaign_psu_logs.loadData(psu_rows)
    
    if campaign_psu_logs.searchVoltageSpike() == -1:
        return -1
    
    campaign_psu_logs.calculateTimePsuAndPower()
    campaign_psu_logs.findTwoMaxValues()

    psuRawPlot(psu_logs=campaign_psu_logs.campaign_psu_logs[1].psu_logs, y_min=-0.5, y_max=2)
    
    return 1

if __name__ == "__main__":
    myMain()