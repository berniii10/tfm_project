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
    
    campaign_iot_logs.findHighestFrameAndSlot()
    campaign_iot_logs.getPsuMax()
    campaign_iot_logs.getMcs()


    # PSU
    psu_rows = DbConnection.getDataFromDb(myDb=myDb, campaign_id=campaign_id, iot_psu=0)
    campaign_psu_logs = CampaignPsuLogs()
    campaign_psu_logs.loadData(psu_rows)
    
    if campaign_psu_logs.searchVoltageSpike() == -1:
        return -1
    
    campaign_psu_logs.calculateTimePsuAndPower()
    campaign_psu_logs.findTwoMaxValues()
    return 1
    #iot_logs = IotLogs()
    
    #iot_logs = IotLogs()
    #if iot_logs.loadIotData(myDb=myDb, campaignId=186) == -1:
    #    return -1

    
    #foundPrach = iot_logs.searchPrach()
    #if foundPrach == -1:
    #    return -1
    
    #for iot_log in iot_logs.iot_logs:
    #    if iot_log.frame == -1 and iot_log.layer == Layer.PHY:
    #        print("Phy with -1")

    #iot_logs.findHighestFrameAndSlot()
    #iot_logs.sortPhyLogEntries()
    #iot_logs.sortNonPhyLogEntries()
        
    #psu_rows = DbConnection.getDataFromDb(myDb=myDb, campaign_id=186, iot_psu=0)
    #psu_logs = PsuLogs()
    #if psu_logs.loadPsuData(myDb=myDb, campaignId=186) == -1:
    #    return -1
    
    #dict = {}
    #for psu_log in psu_logs.psu_logs:
    #    if psu_log.resulttypeid in dict:
    #        # If the key exists, increment its value by 1
    #        dict[psu_log.resulttypeid] += 1
    #    else:
    #        # If the key doesn't exist, initialize it with a value of 1
    #        dict[psu_log.resulttypeid] = 1

    #foundVoltageSpike = psu_logs.searchVoltageSPike()
    #if foundVoltageSpike == -1:
    #    return -1

    #psu_logs.calculateTimePsuAndPower()


    #psuRawPlot(psu_logs=psu_logs)

if __name__ == "__main__":
    myMain()