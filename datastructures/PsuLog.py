from psycopg2 import Error

def getPsuQuery(CampaignId):
    return "with testrunCampaign as (select testrun.runid from testrun inner join testrun2params on testrun.runid = testrun2params.runid inner join params on testrun2params.paramid = params.paramid inner join resultseries on testrun.runid = resultseries.runid inner join resulttype on resulttype.resulttypeid = resultseries.resulttypeid where testrun.runid in (select distinct testrun.runid from (select testrun.testrunguid from testrun inner join planrun on planrun.runid = testrun.runid where planrun.planrunnumber = "+str(CampaignId)+" /*CampaignId*/) as guid inner join params on cast(guid.testrunguid as text)= params.value inner join testrun2params on params.paramid = testrun2params.paramid	inner join testrun on testrun.runid = testrun2params.runid where testrun.planrunid is not null) and params.name = 'Verdict' and params.value = 'Pass' and resulttype.name like 'TX_PSU%') select resulttype.resulttypeid, result.dim0 as \"StartTime\",	result.dim2 as \"Amperes\", result.dim3 as \"Volts\", result.dim6 as \"Origin\" from (resulttype inner join resultseries on resulttype.resulttypeid = resultseries.resulttypeid inner join result on result.resultseriesid = resultseries.resultseriesid) inner join testrun on testrun.runid = resultseries.runid where testrun.runid in (select * from testrunCampaign) order by result.resultid asc;"


class PsuLogs:
    def __init__(self, resulttypeid, starttime, amperes, volts, origin):
        self.resulttypeid = int(resulttypeid)
        self.starttime = float(starttime)
        self.amperes = float(amperes)
        self.volts = float(volts)
        self.origin = float(origin)
        

def loadPsuData(myDb, campaignId):
    print("Loading PSU Data")
    try:
        cursor = myDb.cursor()

        cursor.execute(getPsuQuery(campaignId))
        rows = cursor.fetchall()

        # Process the result set and create instances of PsuLogs class
        psu_logs = [PsuLogs(*row) for row in rows]

        # Close the cursor and connection
        cursor.close()

        print("PSU Data loaded correctly")
        return psu_logs

    except Error as e:
        print(f"Error: {e}")
        return -1