import sys
import re
from psycopg2 import Error
from datastructures.enums import *


class CampaignIotLogs:
    
    def __init__(self):
        self.campaign_iot_logs = []

    def howManyTestplans(self):
        return len(self.campaign_iot_logs)

    def loadIotData(self, rows):
        indexes = {}
        temp_iot_logs = {}

        for row in rows:
            resulttypeid = int(row[0])

            if resulttypeid in indexes:
                indexes[resulttypeid] += 1

            else:
                indexes[resulttypeid] = 0

            if resulttypeid in temp_iot_logs:
                temp_iot_logs[resulttypeid].append(IotLog(*row, indexes[resulttypeid]))

            else:
                temp_iot_logs[resulttypeid] = []
                temp_iot_logs[resulttypeid].append(IotLog(*row, indexes[resulttypeid]))

        self.campaign_iot_logs = [IotLogs(iot_logs=temp_iot_logs[key]) for key in temp_iot_logs]
        print("IoT Data loaded correctly")
        return 1
    
    def searchPrach(self):
        for campaign_iot_log in self.campaign_iot_logs:
            campaign_iot_log.searchPrach()
            
    def updateTimeStamp(self):
        for campaign_iot_log in self.campaign_iot_logs:
            campaign_iot_log.updateTimeStamp()    
    
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

    def getPsuMax(self):
        for campaign_iot_log in self.campaign_iot_logs:
            campaign_iot_log.getPsuMax()

    def cleanData(self):
        for campaign_iot_log in self.campaign_iot_logs:
            campaign_iot_log.cleanData()

    def getMcs(self):
        for campaign_iot_log in self.campaign_iot_logs:
            campaign_iot_log.getMcs()

    def getMimo(self):
        for campaign_iot_log in self.campaign_iot_logs:
            campaign_iot_log.getMimo()

    def getFrequencyBand(self):
        for campaign_iot_log in self.campaign_iot_logs:
            campaign_iot_log.getFrequencyBand()

    def getAllNas(self):
        for campaign_iot_log in self.campaign_iot_logs:
            campaign_iot_log.getAllNas()

    def getRegistrationCompleteIndexTime(self):
        for campaign_iot_log in self.campaign_iot_logs:
            campaign_iot_log.getRegistrationCompleteIndexTime()

class IotLogs:

    def __init__(self, iot_logs=None):

        self.iot_logs = []

        self.phy_indexes = []
        self.phy_sib_indexes = []
        self.phy_nonsib_indexes = []
        self.non_phy_indexes = []

        self.phy_time_in_secs_and_indexes_list = []
        self.non_phy_time_stamps_secs = []

        self.p_max = 0
        self.mcs_index = 0
        self.mcs_table = ''
        self.mimo = 1
        self.bw = 0
        self.freq_band = 0

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
        
        elif iot_log.layer != Layer.RLC and iot_log.direction != Direction.NA and iot_log.layer != Layer.S1AP:
            self.non_phy_indexes.append(iot_log.index)

        else:
            pass

    def loadIotData(self, iot_logs):

        for iot_log in iot_logs:
            self.addIotLog(iot_log)
        
        if len(self.phy_indexes) == 0:
            print("No PHY log entries found in the Iot log")
            return -1

        return 1

    def sortPhyLogEntries(self):

        calctime = 0.0
        hfn = 0; #*10240 ms
        frame = 0; #*10 ms
        slot = 0.0; #*0.5 ms
        distance = 0
        offsetTimestamp = float(self.iot_logs[0].frame * 10 + self.iot_logs[0].slot * 0.5)
        biggestFrameForCurrentHfn = self.iot_logs[0].frame

        for i in range (0, len(self.phy_indexes), 1):
            if i > 2666:
                pass
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
                # Find the max index value in phy_nonsib_indexes that are still less than non_phy_indexes[i]
                for u in range(len(self.phy_nonsib_indexes)-1, 0, -1):
                    if (self.non_phy_indexes[i] > self.phy_nonsib_indexes[u]):

                        indexOfPhyLayerEquivalentLogEntry = self.phy_nonsib_indexes[u]; # We do not need to check if phy_nonsib_indexes[0] is bigger than non_phy_indexes[i] since that is already taken care of in "Check for DUT activity before PRACH" above
                        break; # Break for loop
                    
                if (indexOfPhyLayerEquivalentLogEntry == -1):

                    print("Rogue Non-PHY message detected")
                    return -1
            
            elif self.iot_logs[self.non_phy_indexes[i]].direction == Direction.DL and (self.iot_logs[self.non_phy_indexes[i]].layer == Layer.MAC or self.iot_logs[self.non_phy_indexes[i]].layer == Layer.RRC or self.iot_logs[self.non_phy_indexes[i]].layer == Layer.NAS):
            
                # Find the max index value in phy_nonsib_indexes that are still less than non_phy_indexes[i]
                if "SIB" in self.iot_logs[self.non_phy_indexes[i]].message:
                    for u in range(0, len(self.phy_sib_indexes), 1):
                        if (self.non_phy_indexes[i] < self.phy_sib_indexes[u]):

                            indexOfPhyLayerEquivalentLogEntry = self.phy_sib_indexes[u]
                            break; # Break for loop
                else:
                    for u in range(0, len(self.phy_nonsib_indexes), 1):
                        if (self.non_phy_indexes[i] < self.phy_nonsib_indexes[u] and "dci" in self.iot_logs[self.phy_nonsib_indexes[u]].message):
                        
                            indexOfPhyLayerEquivalentLogEntry = self.phy_nonsib_indexes[u]
                            break; # Break for loop
                        
                if (indexOfPhyLayerEquivalentLogEntry == -1):

                    self.non_phy_time_stamps_secs.append((sys.float_info.max/10, self.non_phy_indexes[i])) # This is only when LittleOne cuts the log in the end - in that case we just set timestamp to max value since we can't find the matching Phy timestamp
                    continue
            
            else:
                print("Unknown Non-PHY log entry. Layer=\"{self.iot_logs[self.non_phy_indexes[i]].layer}\". Direction=\"{self.iot_logs[self.non_phy_indexes[i]].direction}\"")
                return -1 
            
            for u in range(0, len(self.phy_time_in_secs_and_indexes_list), 1):
                if (self.phy_time_in_secs_and_indexes_list[u][1] == indexOfPhyLayerEquivalentLogEntry): # This will always be true with one of the indexes so we do not need to check if we actually found a match later
                    
                    self.non_phy_time_stamps_secs.append((self.phy_time_in_secs_and_indexes_list[u][0], self.non_phy_indexes[i]))
                    break; # Break for loop
            
            
        self.non_phy_time_stamps_secs = sorted(self.non_phy_time_stamps_secs, key=lambda x: x[0]) #Could also include the .Value like: phy_time_in_secs_and_indexes_list.OrderBy(e => e.Key).ThenBy(e => e.Value).ToList();

    def cleanData(self):
        tmp_clean_sorted_timestamped_data = []

        cleanedSortedAndTimestampedIndex = 0
        phyIndex = 0
        nonPhyIndex = 0

        while phyIndex < len(self.phy_time_in_secs_and_indexes_list) and nonPhyIndex < len(self.non_phy_indexes):
            if (self.phy_time_in_secs_and_indexes_list[phyIndex][0] == self.non_phy_time_stamps_secs[nonPhyIndex][0] and self.iot_logs[self.non_phy_time_stamps_secs[nonPhyIndex][1]].direction == Direction.UL) or self.phy_time_in_secs_and_indexes_list[phyIndex][0] < self.non_phy_time_stamps_secs[nonPhyIndex][0]:
                tmp_clean_sorted_timestamped_data.append(IotLog(self.iot_logs[self.phy_time_in_secs_and_indexes_list[phyIndex][1]].resulttypeid,
                                                                self.iot_logs[self.phy_time_in_secs_and_indexes_list[phyIndex][1]].timestamp,
                                                                self.iot_logs[self.phy_time_in_secs_and_indexes_list[phyIndex][1]].absolutetime,
                                                                self.iot_logs[self.phy_time_in_secs_and_indexes_list[phyIndex][1]].frame,
                                                                self.iot_logs[self.phy_time_in_secs_and_indexes_list[phyIndex][1]].slot,
                                                                self.iot_logs[self.phy_time_in_secs_and_indexes_list[phyIndex][1]].ue_id,
                                                                self.iot_logs[self.phy_time_in_secs_and_indexes_list[phyIndex][1]].layer,
                                                                self.iot_logs[self.phy_time_in_secs_and_indexes_list[phyIndex][1]].info,
                                                                self.iot_logs[self.phy_time_in_secs_and_indexes_list[phyIndex][1]].direction,
                                                                self.iot_logs[self.phy_time_in_secs_and_indexes_list[phyIndex][1]].message,
                                                                self.iot_logs[self.phy_time_in_secs_and_indexes_list[phyIndex][1]].extrainfo,
                                                                self.iot_logs[self.phy_time_in_secs_and_indexes_list[phyIndex][1]].index,
                                                                self.phy_time_in_secs_and_indexes_list[phyIndex][0]))
                cleanedSortedAndTimestampedIndex += 1
                phyIndex += 1
            
            elif (self.phy_time_in_secs_and_indexes_list[phyIndex][0] == self.non_phy_time_stamps_secs[nonPhyIndex][0] and self.iot_logs[self.non_phy_time_stamps_secs[nonPhyIndex][1]].direction == Direction.DL) or self.phy_time_in_secs_and_indexes_list[phyIndex][0] > self.non_phy_time_stamps_secs[nonPhyIndex][0]:
                tmp_clean_sorted_timestamped_data.append(IotLog(self.iot_logs[self.non_phy_indexes[nonPhyIndex]].resulttypeid,
                                                                self.iot_logs[self.non_phy_indexes[nonPhyIndex]].timestamp,
                                                                self.iot_logs[self.non_phy_indexes[nonPhyIndex]].absolutetime,
                                                                self.iot_logs[self.non_phy_indexes[nonPhyIndex]].frame,
                                                                self.iot_logs[self.non_phy_indexes[nonPhyIndex]].slot,
                                                                self.iot_logs[self.non_phy_indexes[nonPhyIndex]].ue_id,
                                                                self.iot_logs[self.non_phy_indexes[nonPhyIndex]].layer,
                                                                self.iot_logs[self.non_phy_indexes[nonPhyIndex]].info,
                                                                self.iot_logs[self.non_phy_indexes[nonPhyIndex]].direction,
                                                                self.iot_logs[self.non_phy_indexes[nonPhyIndex]].message,
                                                                self.iot_logs[self.non_phy_indexes[nonPhyIndex]].extrainfo,
                                                                self.iot_logs[self.non_phy_indexes[nonPhyIndex]].index,
                                                                self.non_phy_time_stamps_secs[nonPhyIndex][0]))
                cleanedSortedAndTimestampedIndex += 1
                nonPhyIndex += 1

                
        while phyIndex < len(self.phy_time_in_secs_and_indexes_list) :
            tmp_clean_sorted_timestamped_data.append(IotLog(self.iot_logs[self.phy_time_in_secs_and_indexes_list[phyIndex][1]].resulttypeid,                    ## Can't we change this for <or> in previous loop instead or <and>?
                                                                self.iot_logs[self.phy_time_in_secs_and_indexes_list[phyIndex][1]].timestamp,
                                                                self.iot_logs[self.phy_time_in_secs_and_indexes_list[phyIndex][1]].absolutetime,
                                                                self.iot_logs[self.phy_time_in_secs_and_indexes_list[phyIndex][1]].frame,
                                                                self.iot_logs[self.phy_time_in_secs_and_indexes_list[phyIndex][1]].slot,
                                                                self.iot_logs[self.phy_time_in_secs_and_indexes_list[phyIndex][1]].ue_id,
                                                                self.iot_logs[self.phy_time_in_secs_and_indexes_list[phyIndex][1]].layer,
                                                                self.iot_logs[self.phy_time_in_secs_and_indexes_list[phyIndex][1]].info,
                                                                self.iot_logs[self.phy_time_in_secs_and_indexes_list[phyIndex][1]].direction,
                                                                self.iot_logs[self.phy_time_in_secs_and_indexes_list[phyIndex][1]].message,
                                                                self.iot_logs[self.phy_time_in_secs_and_indexes_list[phyIndex][1]].extrainfo,
                                                                self.iot_logs[self.phy_time_in_secs_and_indexes_list[phyIndex][1]].index,
                                                                self.phy_time_in_secs_and_indexes_list[phyIndex][0]))
            cleanedSortedAndTimestampedIndex += 1
            phyIndex += 1
        
        # Copy the rest from nonPhyIndexes if not done in previous loop
        while nonPhyIndex < len(self.non_phy_indexes):
            if (self.non_phy_time_stamps_secs[nonPhyIndex][0] == sys.float_info.max):
                continue; # Log does not have a real timestamp might be due to the measurement being cut
            
            tmp_clean_sorted_timestamped_data.append(IotLog(self.iot_logs[self.non_phy_indexes[nonPhyIndex]].resulttypeid,
                                                                self.iot_logs[self.non_phy_indexes[nonPhyIndex]].timestamp,
                                                                self.iot_logs[self.non_phy_indexes[nonPhyIndex]].absolutetime,
                                                                self.iot_logs[self.non_phy_indexes[nonPhyIndex]].frame,
                                                                self.iot_logs[self.non_phy_indexes[nonPhyIndex]].slot,
                                                                self.iot_logs[self.non_phy_indexes[nonPhyIndex]].ue_id,
                                                                self.iot_logs[self.non_phy_indexes[nonPhyIndex]].layer,
                                                                self.iot_logs[self.non_phy_indexes[nonPhyIndex]].info,
                                                                self.iot_logs[self.non_phy_indexes[nonPhyIndex]].direction,
                                                                self.iot_logs[self.non_phy_indexes[nonPhyIndex]].message,
                                                                self.iot_logs[self.non_phy_indexes[nonPhyIndex]].extrainfo,
                                                                self.iot_logs[self.non_phy_indexes[nonPhyIndex]].index,
                                                                self.non_phy_time_stamps_secs[nonPhyIndex][0]))
            cleanedSortedAndTimestampedIndex += 1
            nonPhyIndex += 1

        self.iot_logs = tmp_clean_sorted_timestamped_data
        
    def getPsuMax(self):
        pattern = r'p-Max\s+(\d+)'
        pmax = -50

        for iot_log in self.iot_logs:
            if MessagesRrc.SIB1.value in iot_log.message:
                pmax = re.search(pattern, iot_log.extrainfo)
                if pmax != -50:
                    self.p_max = pmax.group(1)
                    return 1
                
        print("Could not find any P Max value")
        return -1

    def searchPrach(self):
        found = -1
        for i, iot_log in enumerate(self.iot_logs):
            if iot_log.info == 'PRACH':
                found = 1
                print(f"PRACH found at index {i} and time stamp {iot_log.timeIot}")
                self.importantIndexes = ImportantIndexes(i)
                return found
            elif iot_log.direction == Direction:
                print("DUT activity detected before PRACH. Cannot sync PSU and IoT logs.")
                return found

        if found == -1:
            print(f"Could not find IoT PRACH log")
            return found
        
    def updateTimeStamp(self):
        time = self.iot_logs[self.importantIndexes.prach_index].timeIot
        for i, iot_log in enumerate(self.iot_logs):
            iot_log.timeIot = iot_log.timeIot - time

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

    def getMcs(self):
        pattern1 = r'mcs=(\d+)'
        pattern2 = r'mcs-Table\s+([^\s,]+),'
        found1 = 0
        found2 = 0

        for i, iot_log in enumerate(self.iot_logs):

            if iot_log.layer == Layer.NAS and 'Registration request' in iot_log.message and found1 == 0:
                for j in range(i, i+100, 1):

                    if self.iot_logs[j].info == 'PDCCH' and self.iot_logs[j].layer == Layer.PHY and 'dci=0_' in self.iot_logs[j].extrainfo:
                        mcs = re.search(pattern1, self.iot_logs[j].extrainfo)

                        if mcs:
                            self.mcs_index = int(mcs.group(1))
                            found1 = 1
                        

            if iot_log.layer == Layer.RRC and 'RRC reconfiguration' in iot_log.message and found2 == 0:
                mcs = re.search(pattern2, iot_log.extrainfo)

                if mcs:
                    self.mcs_table = mcs.group(1)
                    found2 = 1

    def getMimo(self):
        pattern1 = r'maxMIMO-Layers\s+(\d+)'

        for iot_log in self.iot_logs:

            if iot_log.layer == Layer.RRC and 'RRC reconfiguration' in iot_log.message:
                mimo = re.search(pattern1, iot_log.extrainfo)

                if mimo:
                    self.mimo = mimo.group(1)
                    return 1

    def getFrequencyBand(self):
        pattern = r'freqBandIndicatorNR\s+(\d+)'
        freq_band = -50

        for iot_log in self.iot_logs:
            if MessagesRrc.SIB1.value in iot_log.message:
                freq_band = re.search(pattern, iot_log.extrainfo)
                if freq_band != -50:
                    self.freq_band = int(freq_band.group(1))
                    return 1
                
        print("Could not find any P Max value")
        return -1
    
    def getAllNas(self):

        for iot_log in self.iot_logs:
            if iot_log.layer == Layer.NAS:
                print(iot_log.message)

    def getRegistrationCompleteIndexTime(self):
        for i, iot_log in enumerate(self.iot_logs):
            if iot_log.layer == Layer.NAS and MessagesNas.Registration_complete.value in iot_log.message:
                self.importantIndexes.registration_complete_index = i
                self.importantIndexes.registration_complete_time = iot_log.timeIot

class IotLog:
    def __init__(self, resulttypeid, timestamp, absolutetime, frame, slot, ue_id, layer, info, direction, message, extrainfo, index, timeIot=None):
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
        if timeIot != None:
            self.timeIot = timeIot
        else:
            self.timeIot = 0.0

class ImportantIndexes():
    
    def __init__(self, prach_index):

        self.prach_index = prach_index
        self.prach_time = 0

        self.registration_complete_index = 0
        self.registration_complete_time = 0
        