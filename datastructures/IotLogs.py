import sys
from psycopg2 import Error
from datastructures.enums import *

def getIotQuery(CampaignId):
    return "with testrunCampaign as (select testrun.runid from	testrun inner join testrun2params on testrun.runid = testrun2params.runid inner join params on testrun2params.paramid = params.paramid inner join resultseries on testrun.runid = resultseries.runid inner join resulttype on resulttype.resulttypeid = resultseries.resulttypeid where	testrun.runid in (select distinct testrun.runid	from (select testrun.testrunguid from testrun inner join planrun on planrun.runid = testrun.runid where planrun.planrunnumber = "+str(CampaignId)+" /*CampaignId*/) as guid inner join params on cast(guid.testrunguid as text)= params.value inner join testrun2params on params.paramid = testrun2params.paramid	inner join testrun on testrun.runid = testrun2params.runid where testrun.planrunid is not null) and params.name = 'Verdict'	and params.value = 'Pass' and resulttype.name like 'TX_IoT%') select resulttype.resulttypeid, result.dim0 as \"TimeStamp\",	result.dim2 as \"AbsoluteTime\", result.dim4 as \"RFN\", result.dim5 as \"SFN\",	result.dim6 as \"UE_ID\",	result.dim7 as \"Layer\",	coalesce(nullif(result.dim8,''),'empty') as \"Info\",coalesce(nullif(result.dim9,''),'empty') as \"Direction\",result.dim10 as \"Message\",coalesce(nullif(result.dim11,''),'empty') as \"ExtraInfo\" from (resulttype inner join resultseries on resulttype.resulttypeid = resultseries.resulttypeid inner join result on result.resultseriesid = resultseries.resultseriesid) inner join testrun on testrun.runid = resultseries.runid where testrun.runid in (select * from testrunCampaign) order by result.resultid asc;"

class IotLogs:

    iot_logs = []

    phy_indexes = []
    phy_sib_indexes = []
    phy_nonsib_indexes = []
    non_phy_indexes = []

    phyTimeInSecsAndIndexesList = []
    nonPhyTimeStampsSecs = []

    def __init__(self):
        pass
    
    def addIotLog(self, iot_log):

        self.iot_logs.append(iot_log)

        if iot_log.slot > 0:
            pass

        if iot_log.layer == Layer.PHY:
            self.phy_indexes.append(iot_log.index)

            if iot_log.info == 'PDSCH' and 'harq=si' in iot_log.message:
                self.phy_sib_indexes.append(iot_log.index)
            else:
                self.phy_nonsib_indexes.append(iot_log.index)
        
        elif iot_log.layer != Layer.RLC:
            self.non_phy_indexes.append(iot_log.index)

        else:
            pass

    def loadIotData(self, myDb, campaignId):
        try:
            print("Loading IoT Data")
            cursor = myDb.cursor()

            cursor.execute(getIotQuery(campaignId))
            rows = cursor.fetchall()

            # Process the result set and create instance of IotLogs class
            
            for i, row in enumerate(rows):
                self.addIotLog(IotLog(*row, i))

            # Close the cursor and connection
            cursor.close()
            
            print("IoT Data loaded correctly")

            if len(self.phy_indexes) == 0:
                print("No PHY log entries found in the Iot log")
                return -1

            return 1

        except Error as e:
            print(f"Error: {e}")
            return -1

    def searchPrach(self):
        found = -1
        for phy_iot_log in self.iot_logs:
            if phy_iot_log.info == 'PRACH':
                found = 1
                return found
            elif phy_iot_log.direction == Direction:
                print("DUT activity detected before PRACH. Cannot sync PSU and IoT logs.")
                return found

        if found == 0:
            print(f"Could not find IoT PRACH log")
            return found

    def findHighestFrameAndSlot(self):
        frame = -1
        slot = -1
        for iot_log in self.iot_logs:

            if frame < iot_log.frame:
                frame = iot_log.frame

            if slot < iot_log.slot:
                slot = iot_log.slot

        print(f"Biggest Frame: {frame}. Biggest Slot: {slot}")

    #Now sort the Phy log entries using FRAME and slot and at the same time keep track of the HFN which increases every time FRAME wraps around.
    #Important note: the log entries are not sorted - they can vary several milliseconds. Example: log_entry1=time10, log_entry2=time8, log_entry3=time12
    #The FRAME value range is 0-1023. When FRAME wraps around HFN has to count one up.
    #The algorithm below will accept time difference on 512 * 10 ms in delay of "old" log entries and accept 511 * 10 ms in future (and same FRAME as previous biggest FRAME = 0 ms different).
    #The timestamp is calculated like HFN * 10240ms + FRAME * 10ms + slot * 0.5ms

    #      0 <--------------------------- FRAME range ---------------------------> 1023
    #      |                                                                      |
    #      |  Past 0-511            PrevBiggestFRAME=512     Future 513-1023        |
    #      |  Future 0-510 (HFN+1)  Past 511-1022          PrevBiggestFRAME=1023    |
    #      |  PrevBiggestFRAME=0      Future 1-510           Past 511-1022 (HFN-1)  |

    #Key: calculated timestamp in seconds based on HFN, FRAME, slot
    #Value: index in tapDbDataIoTLog
    def sortPhyLogEntries(self):

        calctime = 0.0
        hfn = 0; #*10240 ms
        frame = 0; #*10 ms
        slot = 0.0; #*0.5 ms
        distance = 0
        offsetTimestamp = float(self.iot_logs[0].frame * 10 + self.iot_logs[0].slot * 0.5)
        biggestFrameForCurrentHfn = self.iot_logs[0].frame

        for i in range (0, len(self.phy_indexes), 1):
            frame = self.iot_logs[self.phy_indexes[i]].frame
            slot  = self.iot_logs[self.phy_indexes[i]].slot

            if (frame < 0 or frame > 1023): #frame value range is 0-1023
                print(f"frame value ({frame}) is out range. Valid range is 0-1023")
                return -1
            
            if (slot < 0 or slot > 19): #slot value range is 0-9
                print(f"slot value ({slot}) is out range. Valid range is 0-9")
                return -1

            distance = frame - biggestFrameForCurrentHfn
            if (distance >= 512):
                #Previous HFN
                calctime = float((hfn - 1) * 10240 + frame * 10 + slot * 0.5 - offsetTimestamp) / 1000; #HFN variable should never move backward in time so we do not update the variable
            
            else:
                if (distance > 0):
                    biggestFrameForCurrentHfn = frame
                
                elif (distance <= -512):
                    #Next HFN due to frame wrap around
                    hfn += 1
                    biggestFrameForCurrentHfn = frame
            
                calctime = float(hfn * 10240 + frame * 10 + slot * 0.5 - offsetTimestamp) / 1000
            
            if (calctime == sys.float_info.max):
                calctime /= 10.0; # Log does not have a real timestamp might be due to the measurement being cut. However to avoid a db overflow we divide by 10
            
            self.phyTimeInSecsAndIndexesList.append((calctime, self.phy_indexes[i]))
        
        #Sort the list by calculated timestamp in seconds based on HFN, frame, slot
        self.phyTimeInSecsAndIndexesList = sorted(self.phyTimeInSecsAndIndexesList, key=lambda x: x[0]) #Could also include the .Value like: phyTimeInSecsAndIndexesList.OrderBy(e => e.Key).ThenBy(e => e.Value).ToList();
        return 1
    
    def sortNonPhyLogEntries(self):
        
        for (int i = 0; i < nonPhyIndexes.Count; i++)
        {
            int indexOfPhyLayerEquivalentLogEntry = -1;
            if (tapDbDataIoTLog.direction[nonPhyIndexes[i]] == "UL" && (tapDbDataIoTLog.layer[nonPhyIndexes[i]] == "MAC" || tapDbDataIoTLog.layer[nonPhyIndexes[i]] == "RRC" || tapDbDataIoTLog.layer[nonPhyIndexes[i]] == "NAS"))
            {
                //Find the max index value in PhyNonSibIndexes that are still less than nonPhyIndexes[i]
                for (int u = phyNonSibIndexes.Count() - 1 ; u > 0 ; u--)
                {
                    if (nonPhyIndexes[i] > phyNonSibIndexes[u])
                    {
                        indexOfPhyLayerEquivalentLogEntry = phyNonSibIndexes[u]; //We do not need to check if PhyNonSibIndexes[0] is bigger than nonPhyIndexes[i] since that is already taken care of in "Check for DUT activity before PRACH" above
                        break; //Break for loop
                    }
                }
                if (indexOfPhyLayerEquivalentLogEntry == -1)
                {
                    errorMessage = $"Rogue Non-PHY message detected";
                    return false;
                }
            }
            else if (tapDbDataIoTLog.direction[nonPhyIndexes[i]] == "DL" && (tapDbDataIoTLog.layer[nonPhyIndexes[i]] == "MAC" || tapDbDataIoTLog.layer[nonPhyIndexes[i]] == "RRC" || tapDbDataIoTLog.layer[nonPhyIndexes[i]] == "NAS"))
            {
                //Find the max index value in PhyNonSibIndexes that are still less than nonPhyIndexes[i]
                if (tapDbDataIoTLog.message[nonPhyIndexes[i]].Contains("SIB") == true)
                {
                    for (int u = 0; u < phySibIndexes.Count; u++)
                    {
                        if (nonPhyIndexes[i] < phySibIndexes[u])
                        {
                            indexOfPhyLayerEquivalentLogEntry = phySibIndexes[u];
                            break; //Break for loop
                        }
                    }
                }
                else
                { 
                    for (int u = 0; u < phyNonSibIndexes.Count; u++)
                    {
                        if (nonPhyIndexes[i] < phyNonSibIndexes[u] && tapDbDataIoTLog.message[phyNonSibIndexes[u]].Contains("dci") == false)
                        {
                            indexOfPhyLayerEquivalentLogEntry = phyNonSibIndexes[u];
                            break; //Break for loop
                        }
                    }
                }
                if (indexOfPhyLayerEquivalentLogEntry == -1)
                {
                    nonPhyTimeStampsSecs.Add(new KeyValuePair<double, int>(double.MaxValue/10, nonPhyIndexes[i])); //This is only when LittleOne cuts the log in the end - in that case we just set timestamp to max value since we can't find the matching Phy timestamp
                    continue;
                }
            }
            else
            {
                errorMessage = $"Unknown Non-PHY log entry. Layer=\"{tapDbDataIoTLog.layer[nonPhyIndexes[i]]}\". Direction=\"{tapDbDataIoTLog.direction[nonPhyIndexes[i]]}\"";
                return false;
            }

            //nonPhyTimeStampsSecs.Add(new KeyValuePair<double, int>(-1.0, nonPhyIndexes[i]));
            for (int u = 0; u < phyTimeInSecsAndIndexesList.Count; u++)
            {
                if (phyTimeInSecsAndIndexesList[u].Value == indexOfPhyLayerEquivalentLogEntry) //This will always be true with one of the indexes so we do not need to check if we actually found a match later
                {
                    nonPhyTimeStampsSecs.Add(new KeyValuePair<double, int>(phyTimeInSecsAndIndexesList[u].Key, nonPhyIndexes[i])); 
                    break; //Break for loop
                }
            }
        }
        nonPhyTimeStampsSecs = nonPhyTimeStampsSecs.OrderBy(e => e.Key).ToList(); //Could also include the .Value like: phyTimeInSecsAndIndexesList.OrderBy(e => e.Key).ThenBy(e => e.Value).ToList();


class IotLog:
    def __init__(self, resulttypeid, timestamp, absolutetime, frame, slot, ue_id, layer, info, direction, message, extrainfo, index):
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
        self.index = index