import psycopg2
from psycopg2 import Error

def getIotQuery(CampaignId):
    return "with testrunCampaign as (select testrun.runid from	testrun inner join testrun2params on testrun.runid = testrun2params.runid inner join params on testrun2params.paramid = params.paramid inner join resultseries on testrun.runid = resultseries.runid inner join resulttype on resulttype.resulttypeid = resultseries.resulttypeid where	testrun.runid in (select distinct testrun.runid	from (select testrun.testrunguid from testrun inner join planrun on planrun.runid = testrun.runid where planrun.planrunnumber = "+str(CampaignId)+" /*CampaignId*/) as guid inner join params on cast(guid.testrunguid as text)= params.value inner join testrun2params on params.paramid = testrun2params.paramid	inner join testrun on testrun.runid = testrun2params.runid where testrun.planrunid is not null) and params.name = 'Verdict'	and params.value = 'Pass' and resulttype.name like 'TX_IoT%') select resulttype.resulttypeid, result.dim0 as \"TimeStamp\",	result.dim2 as \"AbsoluteTime\", result.dim4 as \"RFN\", result.dim5 as \"SFN\",	result.dim6 as \"UE_ID\",	result.dim7 as \"Layer\",	coalesce(nullif(result.dim8,''),'empty') as \"Info\",coalesce(nullif(result.dim9,''),'empty') as \"Direction\",result.dim10 as \"Message\",coalesce(nullif(result.dim11,''),'empty') as \"ExtraInfo\" from (resulttype inner join resultseries on resulttype.resulttypeid = resultseries.resulttypeid inner join result on result.resultseriesid = resultseries.resultseriesid) inner join testrun on testrun.runid = resultseries.runid where testrun.runid in (select * from testrunCampaign) order by result.resultid asc;"

def getPsuQuery(CampaignId):
    return "with testrunCampaign as (select testrun.runid from testrun inner join testrun2params on testrun.runid = testrun2params.runid inner join params on testrun2params.paramid = params.paramid inner join resultseries on testrun.runid = resultseries.runid inner join resulttype on resulttype.resulttypeid = resultseries.resulttypeid where testrun.runid in (select distinct testrun.runid from (select testrun.testrunguid from testrun inner join planrun on planrun.runid = testrun.runid where planrun.planrunnumber = "+str(CampaignId)+" /*CampaignId*/) as guid inner join params on cast(guid.testrunguid as text)= params.value inner join testrun2params on params.paramid = testrun2params.paramid	inner join testrun on testrun.runid = testrun2params.runid where testrun.planrunid is not null) and params.name = 'Verdict' and params.value = 'Pass' and resulttype.name like 'TX_PSU%') select resulttype.resulttypeid, result.dim0 as \"StartTime\",	result.dim2 as \"Amperes\", result.dim3 as \"Volts\", result.dim6 as \"Origin\" from (resulttype inner join resultseries on resulttype.resulttypeid = resultseries.resulttypeid inner join result on result.resultseriesid = resultseries.resultseriesid) inner join testrun on testrun.runid = resultseries.runid where testrun.runid in (select * from testrunCampaign) order by result.resultid asc;"

def connectToDb():
    try:
        myDb = psycopg2.connect(
            user='admin', 
            password='alliot',
            host='alliot-kontrondev.alb.is.keysight.com',
            database='alliot-raw_meas',
            port=5432,
            connect_timeout=100)
        
        if myDb is None:
             print("Failed to connect to DB")
        else:
            print("Success connecting to DB")
            return myDb
        
    except psycopg2.Error as e:
        print(f"Error: {e}")

def getDataFromDb(myDb, campaign_id, iot_psu):
    try:
        cursor = myDb.cursor()

        if iot_psu == 1:
            print("Loading IoT Data")
            cursor.execute(getIotQuery(campaign_id))

        else:
            print("Loading Psu Data")
            cursor.execute(getPsuQuery(campaign_id))

        # Get all rows
        rows = cursor.fetchall()

        # Close the cursor and connection
        cursor.close()
        
        print("Data fetched correctly")
        return rows

    except Error as e:
        print(f"Error: {e}")
        return -1

def closeConnection(myDb):
    myDb.close()