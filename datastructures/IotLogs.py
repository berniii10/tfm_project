from psycopg2 import Error
from datastructures.enums import *

def getIotQuery(CampaignId):
    return "with testrunCampaign as (select testrun.runid from	testrun inner join testrun2params on testrun.runid = testrun2params.runid inner join params on testrun2params.paramid = params.paramid inner join resultseries on testrun.runid = resultseries.runid inner join resulttype on resulttype.resulttypeid = resultseries.resulttypeid where	testrun.runid in (select distinct testrun.runid	from (select testrun.testrunguid from testrun inner join planrun on planrun.runid = testrun.runid where planrun.planrunnumber = "+str(CampaignId)+" /*CampaignId*/) as guid inner join params on cast(guid.testrunguid as text)= params.value inner join testrun2params on params.paramid = testrun2params.paramid	inner join testrun on testrun.runid = testrun2params.runid where testrun.planrunid is not null) and params.name = 'Verdict'	and params.value = 'Pass' and resulttype.name like 'TX_IoT%') select resulttype.resulttypeid, result.dim0 as \"TimeStamp\",	result.dim2 as \"AbsoluteTime\", result.dim4 as \"RFN\", result.dim5 as \"SFN\",	result.dim6 as \"UE_ID\",	result.dim7 as \"Layer\",	coalesce(nullif(result.dim8,''),'empty') as \"Info\",coalesce(nullif(result.dim9,''),'empty') as \"Direction\",result.dim10 as \"Message\",coalesce(nullif(result.dim11,''),'empty') as \"ExtraInfo\" from (resulttype inner join resultseries on resulttype.resulttypeid = resultseries.resulttypeid inner join result on result.resultseriesid = resultseries.resultseriesid) inner join testrun on testrun.runid = resultseries.runid where testrun.runid in (select * from testrunCampaign) order by result.resultid asc;"

class IotLogs:

    phy_log = []
    mac_log = []
    rrc_log = []
    rlc_log = []
    nas_log = []

    def __init__(self):
        pass
    
    def addIotLog(self, iot_log):

        if iot_log.layer == Layer.PHY:
            self.phy_log.append(iot_log)

        elif iot_log.layer == Layer.MAC:
            self.mac_log.append(iot_log)

        elif iot_log.layer == Layer.RRC:
            self.rrc_log.append(iot_log)

        elif iot_log.layer == Layer.RLC:
            self.rlc_log.append(iot_log)

        elif iot_log.layer == Layer.NAS:
            self.nas_log.append(iot_log)

class IotLog:
    def __init__(self, resulttypeid, timestamp, absolutetime, frame, slot, ue_id, layer, info, direction, message, extrainfo):
        self.resulttypeid = int(resulttypeid)
        self.timestamp = int(timestamp)
        self.absolutetime = float(absolutetime)
        self.frame = int(frame)
        self.slot = int(slot)
        self.ue_id = int(ue_id)
        self.layer = Layer(layer)
        self.info = info
        self.direction = Direction(direction)
        self.message = message
        self.extrainfo = extrainfo


def loadIotData(myDb, campaignId):
    try:
        print("Loading IoT Data")
        cursor = myDb.cursor()

        cursor.execute(getIotQuery(campaignId))
        rows = cursor.fetchall()

        # Process the result set and create instance of IotLogs class
        iot_logs = IotLogs()
        for row in rows:
            iot_logs.addIotLog(IotLog(*row))

        # Close the cursor and connection
        cursor.close()
        
        print("IoT Data loaded correctly")
        return iot_logs

    except Error as e:
        print(f"Error: {e}")
        return -1