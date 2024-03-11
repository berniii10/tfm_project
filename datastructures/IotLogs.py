import sys
from psycopg2 import Error
from datastructures.enums import *


class CampaignIotLogs:
    
    campaign_iot_logs = []

    def __init__(self):
        pass

    def howManyTestplans(self):
        return len(self.campaign_iot_logs)

    def loadIotData(self, rows):
        indexes = {}
        temp_iot_logs = {}

        for i, row in enumerate(rows):

            resulttypeid = int(row[0])
            if resulttypeid in indexes:
                indexes[resulttypeid] += 1

            else:
                indexes[resulttypeid] = 0

            if resulttypeid in temp_iot_logs:
                temp_iot_logs[resulttypeid].append(IotLog(*row, indexes[resulttypeid]))
            else:
                temp_iot_logs[resulttypeid] = []

        self.campaign_iot_logs  = [IotLogs() for i in range(len(temp_iot_logs))]

        for i, key in enumerate(temp_iot_logs):
            self.campaign_iot_logs[i].loadIotData(temp_iot_logs[key])

        return 1
    
    def searchPrach(self):
        for campaign_iot_log in self.campaign_iot_logs:
            if campaign_iot_log.searchPrach() == -1:
                return -1
            
    def searchSib(self):
        for campaign_iot_log in self.campaign_iot_logs:
            campaign_iot_log.searchSib()

    def findHighestFrameAndSlot(self):
        for campaign_iot_log in self.campaign_iot_logs:
            campaign_iot_log.findHighestFrameAndSlot()

    def sortPhyLogEntries(self):
        for campaign_iot_log in self.campaign_iot_logs:
            campaign_iot_log.sortPhyLogEntries()

    def sortNonPhyLogEntries(self):
        for campaign_iot_log in self.campaign_iot_logs:
            campaign_iot_log.sortNonPhyLogEntries()


class IotLogs:

    iot_logs = []

    phy_indexes = []
    phy_sib_indexes = []
    phy_nonsib_indexes = []
    non_phy_indexes = []

    phy_time_in_secs_and_indexes_list = []
    nonPhyTimeStampsSecs = []

    psu_max = 0
    mcs_index = 0
    mimo = 1
    bw = 0

    def __init__(self, iot_logs=None):
        if iot_logs != None:
            self.loadIotData(iot_logs=iot_logs)
    
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
        
        elif iot_log.layer != Layer.RLC and iot_log.direction != '- ' and iot_log.layer != Layer.S1AP:
            self.non_phy_indexes.append(iot_log.index)

        else:
            pass

    def loadIotData(self, iot_logs):

        for iot_log in iot_logs:
            self.addIotLog(iot_log)
        
        if len(self.phy_indexes) == 0:
            print("No PHY log entries found in the Iot log")
            return -1

        print("IoT Data loaded correctly")
        return 1

    def searchPrach(self):
        found = -1
        for phy_iot_log in self.iot_logs:
            if phy_iot_log.info == 'PRACH':
                found = 1
                return found
            elif phy_iot_log.direction == Direction:
                print("DUT activity detected before PRACH. Cannot sync PSU and IoT logs.")
                return found

        if found == -1:
            print(f"Could not find IoT PRACH log")
            return found

    def searchSib(self):
        for iot_log in self.iot_logs:
            if "sib" in iot_log.message.lower() or "harq=si" in iot_log.message.lower():
                pass
            if "sib" in iot_log.extrainfo.lower() or "harq=si" in iot_log.message.lower():
                pass

    def findHighestFrameAndSlot(self):
        frame = -1
        slot = -1
        for iot_log in self.iot_logs:

            if frame < iot_log.frame:
                frame = iot_log.frame

            if slot < iot_log.slot:
                slot = iot_log.slot

        print(f"Result Type ID: {self.iot_logs[0].resulttypeid}. Biggest Frame: {frame}. Biggest Slot: {slot}")

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
            
            self.phy_time_in_secs_and_indexes_list.append((calctime, self.phy_indexes[i]))
        
        #Sort the list by calculated timestamp in seconds based on HFN, frame, slot
        self.phy_time_in_secs_and_indexes_list = sorted(self.phy_time_in_secs_and_indexes_list, key=lambda x: x[0]) #Could also include the .Value like: phy_time_in_secs_and_indexes_list.OrderBy(e => e.Key).ThenBy(e => e.Value).ToList();
        return 1
    
    def sortNonPhyLogEntries(self):
        
        for i in range (0, len(self.non_phy_indexes), 1):
            indexOfPhyLayerEquivalentLogEntry = -1
            if self.iot_logs[self.non_phy_indexes[i]].direction == Direction.UL and (self.iot_logs[self.non_phy_indexes[i]].layer == Layer.MAC or self.iot_logs[self.non_phy_indexes[i]].layer == Layer.RRC or self.iot_logs[self.non_phy_indexes[i]].layer == Layer.NAS):
                # Find the max index value in PhyNonSibIndexes that are still less than non_phy_indexes[i]
                for u in range(len(self.phyNonSibIndexes-1, 0, -1)):
                    if (self.non_phy_indexes[i] > self.phyNonSibIndexes[u]):

                        indexOfPhyLayerEquivalentLogEntry = self.phyNonSibIndexes[u]; # We do not need to check if PhyNonSibIndexes[0] is bigger than non_phy_indexes[i] since that is already taken care of in "Check for DUT activity before PRACH" above
                        break; # Break for loop
                    
                if (indexOfPhyLayerEquivalentLogEntry == -1):

                    print("Rogue Non-PHY message detected")
                    return -1
            
            elif self.iot_logs[self.non_phy_indexes[i]].direction == Direction.DL and (self.iot_logs[self.non_phy_indexes[i]].layer == Layer.MAC or self.iot_logs[self.non_phy_indexes[i]].layer == Layer.RRC or self.iot_logs[self.non_phy_indexes[i]].layer == Layer.NAS):
            
                # Find the max index value in PhyNonSibIndexes that are still less than non_phy_indexes[i]
                if "SIB" in self.iot_logs[self.non_phy_indexes[i]].message:
                    for u in range(0, len(self.phy_sib_indexes), 1):
                        if (self.non_phy_indexes[i] < self.phy_sib_indexes[u]):

                            indexOfPhyLayerEquivalentLogEntry = self.phy_sib_indexes[u]
                            break; # Break for loop
                else:
                    for u in range(0, len(self.phyNonSibIndexes), 1):
                        if (self.non_phy_indexes[i] < self.phyNonSibIndexes[u] and "dci" in self.iot_logs[self.phyNonSibIndexes[u]].message):
                        
                            indexOfPhyLayerEquivalentLogEntry = self.phyNonSibIndexes[u]
                            break; # Break for loop
                        
                if (indexOfPhyLayerEquivalentLogEntry == -1):

                    self.nonPhyTimeStampsSecs.append((sys.float_info.max/10, self.non_phy_indexes[i])) # This is only when LittleOne cuts the log in the end - in that case we just set timestamp to max value since we can't find the matching Phy timestamp
                    continue
                
            else:
                print("Unknown Non-PHY log entry. Layer=\"{self.iot_logs[self.non_phy_indexes[i]].layer}\". Direction=\"{self.iot_logs[self.non_phy_indexes[i]].direction}\"")
                return -1 
            
            for u in range(0, len(self.phy_time_in_secs_and_indexes_list), 1):
                if (self.phy_time_in_secs_and_indexes_list[u][1] == indexOfPhyLayerEquivalentLogEntry): # This will always be true with one of the indexes so we do not need to check if we actually found a match later
                    
                    self.nonPhyTimeStampsSecs.append((self.phy_time_in_secs_and_indexes_list[u][0], self.non_phy_indexes[i]))
                    break; # Break for loop
                
            
        self.nonPhyTimeStampsSecs = sorted(self.nonPhyTimeStampsSecs, key=lambda x: x[0]) #Could also include the .Value like: phy_time_in_secs_and_indexes_list.OrderBy(e => e.Key).ThenBy(e => e.Value).ToList();
    

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