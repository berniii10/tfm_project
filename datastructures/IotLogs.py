import sys, re, os, csv, glob, math
import pandas as pd
from scipy.stats import norm
from scipy import stats
import numpy as np
from psycopg2 import Error
from datastructures.enums import *

mcs_table_conversion = {
    'qam64_0': 0,
    'qam64_1': 1,
    'qam64_2': 2,
    'qam64_3': 3,
    'qam64_4': 4,
    'qam64_5': 5,
    'qam64_6': 6,
    'qam64_7': 7,
    'qam64_8': 8,
    'qam64_9': 9,
    'qam64_10': 10,
    'qam64_11': 11,
    'qam64_12': 12,
    'qam64_13': 13,
    'qam64_14': 14,
    'qam64_15': 15,
    'qam64_16': 16,
    'qam64_17': 17,
    'qam64_18': 18,
    'qam64_19': 19,
    'qam64_20': 20,
    'qam64_21': 21,
    'qam64_22': 22,
    'qam64_23': 23,
    'qam64_24': 24,
    'qam64_25': 25,
    'qam64_26': 26,
    'qam64_27': 27,
    'qam64_28': 28,
    'qam256_0': 29,
    'qam256_1': 30,
    'qam256_2': 31,
    'qam256_3': 32,
    'qam256_4': 33,
    'qam256_5': 34,
    'qam256_6': 35,
    'qam256_7': 36,
    'qam256_8': 37,
    'qam256_9': 38,
    'qam256_10': 39,
    'qam256_11': 40,
    'qam256_12': 41,
    'qam256_13': 42,
    'qam256_14': 43,
    'qam256_15': 44,
    'qam256_16': 45,
    'qam256_17': 46,
    'qam256_18': 47,
    'qam256_19': 48,
    'qam256_20': 49,
    'qam256_21': 50,
    'qam256_22': 51,
    'qam256_23': 52,
    'qam256_24': 53,
    'qam256_25': 54,
    'qam256_26': 55,
    'qam256_27': 56
}

class CampaignIotLogs:
    
    def __init__(self):
        self.campaign_iot_logs = []

    def howManyTestplans(self):
        return len(self.campaign_iot_logs)

    def loadIotData(self, rows, sweeps=None):
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

        if sweeps == None:
            self.campaign_iot_logs = [IotLogs(iot_logs=temp_iot_logs[key]) for key in temp_iot_logs]
        else:
            self.campaign_iot_logs = [IotLogs(iot_logs=temp_iot_logs[next(iter(temp_iot_logs))])]

        print("IoT Data loaded correctly")
        return 1
    
    def loadDataFromCsv(self, pmax, mcs_table, mcs_index, n_antenna_ul, n_antenna_dl):
        temp_psu_logs = []

        matching_files = glob.glob(os.path.join('datastructures','files', 'CampaignOutput', f'TX_IoT_pmax{pmax}_MCS{mcs_table}-{mcs_index}_UL{n_antenna_ul}_DL{n_antenna_dl}*' + '.csv'))
        if matching_files:
            df = pd.read_csv(matching_files[0])
            for i, row in df.iterrows():
                temp_psu_logs.append(IotLog(1, row['TimeStamp'], row['Absolute Time'], row['Frame'], row['Slot'], row['UE_ID'], row['Layer'], row['Info'], row['Direction'], row['Message'], row['Extra Info'], i))

            if len(self.campaign_iot_logs) > 0:
                self.campaign_iot_logs.append(IotLogs(iot_logs=temp_psu_logs))
            else:
                self.campaign_iot_logs = [IotLogs(iot_logs=temp_psu_logs)]
        else: 
            print("No matching files found.")
            return -1

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

    def getPMax(self):
        for campaign_iot_log in self.campaign_iot_logs:
            campaign_iot_log.getPMax()

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

    def saveToCsv(self):
        for i, campaign_iot_log in enumerate(self.campaign_iot_logs):
            campaign_iot_log.saveToCsv(i)

    def getPuschTimes(self, lim):
        for campaign_iot_log in self.campaign_iot_logs:
            campaign_iot_log.getPuschTimes(lim)

    def getPdcchTimes(self, lim):
        for campaign_iot_log in self.campaign_iot_logs:
            campaign_iot_log.getPdcchTimes(lim)

    def getPdschTimes(self, lim):
        for campaign_iot_log in self.campaign_iot_logs:
            return campaign_iot_log.getPdschTimes(lim)

    def getPucchTimes(self):
        for campaign_iot_log in self.campaign_iot_logs:
            return campaign_iot_log.getPucchTimes()
        
    def getPsuAssociatedWithResultTypeId(resulttypeid, campaign_psu_logs):
        for campaign_psu_log in campaign_psu_logs.campaign_psu_logs:
            if campaign_psu_log.psu_logs[0].resulttypeid == resulttypeid+1:
                return campaign_psu_log

    def getAllPuschPowers(self, campaign_psu_log):
        for campaign_iot_log, campaign_psu_log in zip(self.campaign_iot_logs, campaign_psu_log.campaign_psu_logs):
            campaign_iot_log.getAllPuschPowers(campaign_psu_log)

    def getAllPdschPowers(self, campaign_psu_log):
        for campaign_iot_log, campaign_psu_log in zip(self.campaign_iot_logs, campaign_psu_log.campaign_psu_logs):
            campaign_iot_log.getAllPdschPowers(campaign_psu_log)
    
    def getMeanAndDeviationPusch(self):
        for campaign_iot_log in self.campaign_iot_logs:
            campaign_iot_log.getMeanAndDeviationPusch()

    def getMeanAndDeviationPdsch(self):
        for campaign_iot_log in self.campaign_iot_logs:
            campaign_iot_log.getMeanAndDeviationPdsch()

    def saveMeanAndDeviationToCsv(self, name):
        all_lists = []
        for campaign_iot_log in self.campaign_iot_logs:
            a = [
                campaign_iot_log.p_max,
                round(campaign_iot_log.p_tx_mean, 3),
                round(campaign_iot_log.p_tx_median, 3),
                round(campaign_iot_log.p_tx_standard_deviation, 3),
                round(campaign_iot_log.p_tx_confidence_interval[0], 3),
                round(campaign_iot_log.p_tx_confidence_interval[1], 3)
            ]
            all_lists.append(a)
        csv_file_path = "meanAndDev" + str(name) + ".csv"

        # Open the CSV file in write mode
        with open(csv_file_path, mode='w', newline='') as file:
            # Create a CSV writer object
            writer = csv.writer(file, delimiter=',')
            writer.writerow(["Pmax", "Mean", "Median", "Standard Deviation", "Confidence Interval Low", "Confidence Interval High"])
            
            # Write the first num_rows_to_save rows from the lists to the CSV file
            for row in all_lists:
                writer.writerow(row)

    def saveDataToCsvForDeepLearningModelPusch(self):
        for campaign_iot_log in self.campaign_iot_logs:
            campaign_iot_log.saveDataForTrainingPusch()

    def saveDataToCsvForDeepLearningModelPdsch(self):
        for campaign_iot_log in self.campaign_iot_logs:
            campaign_iot_log.saveDataForTrainingPdsch()

    def printMcsAndPmax(self):
        for campaign_iot_log in self.campaign_iot_logs:
            print(f"Pmax: {campaign_iot_log.p_max} and MCS: {campaign_iot_log.mcs_index} and Table: {campaign_iot_log.mcs_table}")

class IotLogs:

    def __init__(self, iot_logs=None):

        self.iot_logs = []

        self.phy_indexes = []
        self.phy_sib_indexes = []
        self.phy_nonsib_indexes = []
        self.non_phy_indexes = []

        self.phy_time_in_secs_and_indexes_list = []
        self.non_phy_time_stamps_secs = []

        self.importantIndexes = ImportantIndexes()

        # -------------------------

        self.resulttypeid = []
        self.timestamp = []
        self.absolutetime = []
        self.frame = []
        self.slot = []
        self.ue_id = []
        self.layer = []
        self.info = []
        self.direction = []
        self.message = []
        self.extrainfo = []
        self.index = []
        self.timeIot = []

        # -------------------------

        self.p_max = 0
        self.mcs_index = 0
        self.mcs_table = ''
        self.mimo = 1
        self.bw = 0
        self.freq_band = 0

        self.powers = []
        self.p_tx_mean = 0
        self.p_tx_min = 0
        self.p_tx_max = 0
        self.p_tx_standard_deviation = 0
        self.p_tx_median = 0
        self.p_tx_confidence_interval = 0

        self.powers_pdsch = []
        self.p_rx_mean = 0
        self.p_rx_min = 0
        self.p_rx_max = 0
        self.p_rx_standard_deviation = 0
        self.p_rx_median = 0
        self.p_rx_confidence_interval = 0

        if iot_logs != None:
            self.loadIotData(iot_logs=iot_logs)
    
    def addIotLog(self, iot_log):

        #self.iot_logs.append(iot_log)

        self.resulttypeid.append(iot_log.resulttypeid)
        self.timestamp.append(iot_log.timestamp)
        self.absolutetime.append(iot_log.absolutetime)
        self.frame.append(iot_log.frame)
        self.slot.append(iot_log.slot)
        self.ue_id.append(iot_log.ue_id)
        self.layer.append(iot_log.layer)
        self.info.append(iot_log.info)
        self.direction.append(iot_log.direction)
        self.message.append(iot_log.message)
        self.extrainfo.append(iot_log.extrainfo)
        self.index.append(iot_log.index)
        self.timeIot.append(iot_log.timeIot)

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
        offsetTimestamp = float(self.frame[self.phy_indexes[0]] * 10 + self.slot[self.phy_indexes[0]] * 0.5)
        biggestFrameForCurrentHfn = self.frame[self.phy_indexes[0]]

        for i in range (0, len(self.phy_indexes), 1):
            
            frame = self.frame[self.phy_indexes[i]]
            slot  = self.slot[self.phy_indexes[i]]

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
        print("Sorted Phy Log Entries")
        return 1
    
    def sortNonPhyLogEntries(self):

        # Prepare data in numpy arrays
        non_phy_indexes_tmp = np.array(self.non_phy_indexes)
        phy_nonsib_indexes_tmp = np.array(self.phy_nonsib_indexes)
        phy_sib_indexes_tmp = np.array(self.phy_sib_indexes)

        phy_nonsib_indexes_without_dci = []
        for phy_nonsib_index in self.phy_nonsib_indexes:
            if "dci" not in self.message[phy_nonsib_index]:
                phy_nonsib_indexes_without_dci.append(phy_nonsib_index)
        phy_nonsib_indexes_without_dci_tmp = np.array(phy_nonsib_indexes_without_dci)

        phy_time_in_secs_and_indexes_list_tmp = np.array([item[1] for item in self.phy_time_in_secs_and_indexes_list])

        for i in range (0, len(self.non_phy_indexes), 1):
            indexOfPhyLayerEquivalentLogEntry = -1

            layer = self.layer[self.non_phy_indexes[i]]
            direction = self.direction[self.non_phy_indexes[i]]

            if direction == Direction.UL and (layer == Layer.MAC or layer == Layer.RRC or layer == Layer.NAS):
                # Find the max index value in phy_nonsib_indexes that are still less than non_phy_indexes[i]
                indices = np.where(non_phy_indexes_tmp[i] > phy_nonsib_indexes_tmp)[0]

                if len(indices) > 0:
                    # Get the maximum index
                    max_index = np.max(indices)
                    indexOfPhyLayerEquivalentLogEntry = phy_nonsib_indexes_tmp[max_index]
                else:
                    return -1
                                   
                if (indexOfPhyLayerEquivalentLogEntry == -1):

                    print("Rogue Non-PHY message detected")
                    return -1

            elif direction == Direction.DL and (layer == Layer.MAC or layer == Layer.RRC or layer == Layer.NAS):
                # Find the max index value in phy_nonsib_indexes that are still less than non_phy_indexes[i]
                if "SIB" in self.message[self.non_phy_indexes[i]]:
                    indices = np.where(non_phy_indexes_tmp[i] < phy_sib_indexes_tmp)[0]

                    if len(indices) > 0:
                        # Get the minimum index
                        min_index = np.min(indices)
                        indexOfPhyLayerEquivalentLogEntry = phy_sib_indexes_tmp[min_index]
                    else:
                        indexOfPhyLayerEquivalentLogEntry = phy_sib_indexes_tmp[-1]
                        # return None
                    
                else:
                    indices = np.where(non_phy_indexes_tmp[i] < phy_nonsib_indexes_without_dci_tmp)[0]

                    if len(indices) > 0:
                        # Get the minimum index
                        min_index = np.min(indices)
                        indexOfPhyLayerEquivalentLogEntry = phy_nonsib_indexes_tmp[min_index]
                    else:
                        return -1
                    
                if (indexOfPhyLayerEquivalentLogEntry == -1):

                    self.non_phy_time_stamps_secs.append((sys.float_info.max/10, self.non_phy_indexes[i])) # This is only when LittleOne cuts the log in the end - in that case we just set timestamp to max value since we can't find the matching Phy timestamp
                    continue
                
            else:
                print("Unknown Non-PHY log entry. Layer=\"{self.iot_logs[self.non_phy_indexes[i]].layer}\". Direction=\"{self.iot_logs[self.non_phy_indexes[i]].direction}\"")
                return -1 
            
            # Step 2: Find the index where phy_time_array matches indexOfPhyLayerEquivalentLogEntry
            index = np.where(phy_time_in_secs_and_indexes_list_tmp == indexOfPhyLayerEquivalentLogEntry)[0]

            # Step 3: Append the corresponding tuple to self.non_phy_time_stamps_secs
            if len(index) > 0:
                self.non_phy_time_stamps_secs.append((self.phy_time_in_secs_and_indexes_list[index[0]][0], self.non_phy_indexes[i]))
            
        print("Sorted Non Phy Log entries")
        self.non_phy_time_stamps_secs = sorted(self.non_phy_time_stamps_secs, key=lambda x: x[0]) #Could also include the .Value like: phy_time_in_secs_and_indexes_list.OrderBy(e => e.Key).ThenBy(e => e.Value).ToList();

    def cleanData(self):

        resulttypeid = []
        timestamp = []
        absolutetime = []
        frame = []
        slot = []
        ue_id = []
        layer = []
        info = []
        direction = []
        message = []
        extrainfo = []
        index = []
        timeIot = []

        cleanedSortedAndTimestampedIndex = 0
        phyIndex = 0
        nonPhyIndex = 0

        while phyIndex < len(self.phy_time_in_secs_and_indexes_list) and nonPhyIndex < len(self.non_phy_indexes):
            if (self.phy_time_in_secs_and_indexes_list[phyIndex][0] == self.non_phy_time_stamps_secs[nonPhyIndex][0] and self.direction[self.non_phy_time_stamps_secs[nonPhyIndex][1]] == Direction.UL) or self.phy_time_in_secs_and_indexes_list[phyIndex][0] < self.non_phy_time_stamps_secs[nonPhyIndex][0]:
                
                resulttypeid.append(self.resulttypeid[self.phy_time_in_secs_and_indexes_list[phyIndex][1]])
                timestamp.append(   self.timestamp[self.phy_time_in_secs_and_indexes_list[phyIndex][1]])
                absolutetime.append(self.absolutetime[self.phy_time_in_secs_and_indexes_list[phyIndex][1]])
                frame.append(       self.frame[self.phy_time_in_secs_and_indexes_list[phyIndex][1]])
                slot.append(        self.slot[self.phy_time_in_secs_and_indexes_list[phyIndex][1]])
                ue_id.append(       self.ue_id[self.phy_time_in_secs_and_indexes_list[phyIndex][1]])
                layer.append(       self.layer[self.phy_time_in_secs_and_indexes_list[phyIndex][1]])
                info.append(        self.info[self.phy_time_in_secs_and_indexes_list[phyIndex][1]])
                direction.append(   self.direction[self.phy_time_in_secs_and_indexes_list[phyIndex][1]])
                message.append(     self.message[self.phy_time_in_secs_and_indexes_list[phyIndex][1]])
                extrainfo.append(   self.extrainfo[self.phy_time_in_secs_and_indexes_list[phyIndex][1]])
                index.append(       self.index[self.phy_time_in_secs_and_indexes_list[phyIndex][1]])
                timeIot.append(     self.phy_time_in_secs_and_indexes_list[phyIndex][0])

                cleanedSortedAndTimestampedIndex += 1
                phyIndex += 1
            
            elif (self.phy_time_in_secs_and_indexes_list[phyIndex][0] == self.non_phy_time_stamps_secs[nonPhyIndex][0] and self.direction[self.non_phy_time_stamps_secs[nonPhyIndex][1]] == Direction.DL) or self.phy_time_in_secs_and_indexes_list[phyIndex][0] > self.non_phy_time_stamps_secs[nonPhyIndex][0]:
                
                resulttypeid.append(self.resulttypeid[self.non_phy_indexes[nonPhyIndex]])
                timestamp.append(   self.timestamp[self.non_phy_indexes[nonPhyIndex]])
                absolutetime.append(self.absolutetime[self.non_phy_indexes[nonPhyIndex]])
                frame.append(       self.frame[self.non_phy_indexes[nonPhyIndex]])
                slot.append(        self.slot[self.non_phy_indexes[nonPhyIndex]])
                ue_id.append(       self.ue_id[self.non_phy_indexes[nonPhyIndex]])
                layer.append(       self.layer[self.non_phy_indexes[nonPhyIndex]])
                info.append(        self.info[self.non_phy_indexes[nonPhyIndex]])
                direction.append(   self.direction[self.non_phy_indexes[nonPhyIndex]])
                message.append(     self.message[self.non_phy_indexes[nonPhyIndex]])
                extrainfo.append(   self.extrainfo[self.non_phy_indexes[nonPhyIndex]])
                index.append(       self.index[self.non_phy_indexes[nonPhyIndex]])
                timeIot.append(     self.non_phy_time_stamps_secs[nonPhyIndex][0])

                cleanedSortedAndTimestampedIndex += 1
                nonPhyIndex += 1

                
        while phyIndex < len(self.phy_time_in_secs_and_indexes_list) :
            
            resulttypeid.append(self.resulttypeid[self.phy_time_in_secs_and_indexes_list[phyIndex][1]])
            timestamp.append(   self.timestamp[self.phy_time_in_secs_and_indexes_list[phyIndex][1]])
            absolutetime.append(self.absolutetime[self.phy_time_in_secs_and_indexes_list[phyIndex][1]])
            frame.append(       self.frame[self.phy_time_in_secs_and_indexes_list[phyIndex][1]])
            slot.append(        self.slot[self.phy_time_in_secs_and_indexes_list[phyIndex][1]])
            ue_id.append(       self.ue_id[self.phy_time_in_secs_and_indexes_list[phyIndex][1]])
            layer.append(       self.layer[self.phy_time_in_secs_and_indexes_list[phyIndex][1]])
            info.append(        self.info[self.phy_time_in_secs_and_indexes_list[phyIndex][1]])
            direction.append(   self.direction[self.phy_time_in_secs_and_indexes_list[phyIndex][1]])
            message.append(     self.message[self.phy_time_in_secs_and_indexes_list[phyIndex][1]])
            extrainfo.append(   self.extrainfo[self.phy_time_in_secs_and_indexes_list[phyIndex][1]])
            index.append(       self.index[self.phy_time_in_secs_and_indexes_list[phyIndex][1]])
            timeIot.append(     self.phy_time_in_secs_and_indexes_list[phyIndex][0])
            
            cleanedSortedAndTimestampedIndex += 1
            phyIndex += 1
        
        # Copy the rest from nonPhyIndexes if not done in previous loop
        while nonPhyIndex < len(self.non_phy_indexes):
            if (self.non_phy_time_stamps_secs[nonPhyIndex][0] == sys.float_info.max):
                continue; # Log does not have a real timestamp might be due to the measurement being cut
            
            resulttypeid.append(self.resulttypeid[self.non_phy_indexes[nonPhyIndex]])
            timestamp.append(   self.timestamp[self.non_phy_indexes[nonPhyIndex]])
            absolutetime.append(self.absolutetime[self.non_phy_indexes[nonPhyIndex]])
            frame.append(       self.frame[self.non_phy_indexes[nonPhyIndex]])
            slot.append(        self.slot[self.non_phy_indexes[nonPhyIndex]])
            ue_id.append(       self.ue_id[self.non_phy_indexes[nonPhyIndex]])
            layer.append(       self.layer[self.non_phy_indexes[nonPhyIndex]])
            info.append(        self.info[self.non_phy_indexes[nonPhyIndex]])
            direction.append(   self.direction[self.non_phy_indexes[nonPhyIndex]])
            message.append(     self.message[self.non_phy_indexes[nonPhyIndex]])
            extrainfo.append(   self.extrainfo[self.non_phy_indexes[nonPhyIndex]])
            index.append(       self.index[self.non_phy_indexes[nonPhyIndex]])
            timeIot.append(     self.non_phy_time_stamps_secs[nonPhyIndex][0])
            
            cleanedSortedAndTimestampedIndex += 1
            nonPhyIndex += 1

        self.resulttypeid = resulttypeid
        self.timestamp = timestamp
        self.absolutetime = absolutetime
        self.frame = frame
        self.slot = slot
        self.ue_id = ue_id
        self.layer = layer
        self.info = info
        self.direction = direction
        self.message = message
        self.extrainfo = extrainfo
        self.index = index
        self.timeIot = timeIot
        print("Data Cleaned")
        
    def getPMax(self):
        pattern = r'p-Max\s+(-?\d+)'
        pmax = -50

        for i, message in enumerate(self.message):
            if MessagesRrc.SIB1.value in message:
                pmax = re.search(pattern, self.extrainfo[i])
                if pmax != -50:
                    self.p_max = pmax.group(1)
                    return 1
                
        print("Could not find any P Max value")
        return -1

    def searchPrach(self):
        found = -1
        for i, info in enumerate(self.info):
            if info == 'PRACH':
                found = 1
                print(f"PRACH found at index {i} and time stamp {self.timeIot[i]}")
                self.importantIndexes.prach_index = i
                self.importantIndexes.prach_time = 0
                return found
            elif self.direction[i] == Direction.UL.value:
                print("DUT activity detected before PRACH. Cannot sync PSU and IoT logs.")
                return found

        if found == -1:
            print(f"Could not find IoT PRACH log")
            return found
        
    def updateTimeStamp(self):
        time = self.timeIot[self.importantIndexes.prach_index]
        for i, timeIot in enumerate(self.timeIot):
            self.timeIot[i] = timeIot - time

    def searchSib(self):
        for i, message in enumerate(self.message):
            if "sib" in message.lower() or "harq=si" in message.lower():
                pass
            if "sib" in self.extrainfo[i].lower() or "harq=si" in message.lower():
                pass

    def findHighestFrameAndSlot(self):
        frame_ = -1
        slot_ = -1
        for slot, frame in zip(self.slot, self.frame):

            if frame_ < frame:
                frame_ = frame

            if slot_ < slot:
                slot_ = slot

        print(f"Result Type ID: {self.resulttypeid[0]}. Biggest Frame: {frame}. Biggest Slot: {slot}")

    def getMcs(self):
        pattern1 = r'mcs=(\d+)'
        pattern2 = r'mcs-Table\s+([^\s,]+),'
        found1 = 0
        found2 = 0

        for i, (layer, message, extrainfo) in enumerate(zip(self.layer, self.message, self.extrainfo)):

            if layer == Layer.NAS and 'Registration accept' in message and found1 == 0:
                for j in range(i, i+100, 1):

                    if self.info[j] == 'PDCCH' and self.layer[j] == Layer.PHY and 'dci=0_' in self.extrainfo[j]:
                        mcs = re.search(pattern1, self.extrainfo[j])

                        if mcs:
                            self.mcs_index = int(mcs.group(1))
                            found1 = 1
                            break
                        

            if layer == Layer.RRC and 'RRC reconfiguration' in message and found2 == 0:
                mcs = re.search(pattern2, extrainfo)

                if mcs:
                    self.mcs_table = mcs.group(1)
                    found2 = 1
                else: 
                    self.mcs_table = 'qam64'

    def getMimo(self):
        pattern1 = r'maxMIMO-Layers\s+(\d+)'

        for layer, message, extrainfo in zip(self.layer, self.message, self.extrainfo):

            if layer == Layer.RRC and 'RRC reconfiguration' in message:
                mimo = re.search(pattern1, extrainfo)

                if mimo:
                    self.mimo = mimo.group(1)
                    return 1

    def getFrequencyBand(self):
        pattern = r'freqBandIndicatorNR\s+(\d+)'
        freq_band = -50

        for message, extrainfo in zip(self.message, self.extrainfo):
            if MessagesRrc.SIB1.value in message:
                freq_band = re.search(pattern, extrainfo)
                if freq_band != -50:
                    self.freq_band = int(freq_band.group(1))
                    return 1
                
        print("Could not find any P Max value")
        return -1
    
    def getAllNas(self):

        for layer, message in zip(self.layer, self.message):
            if layer == Layer.NAS:
                print(message)

    def getRegistrationCompleteIndexTime(self):
        for i, (layer, message, timeIot) in enumerate(zip(self.layer, self.message, self.timeIot)):
            if layer == Layer.NAS and MessagesNas.Registration_complete.value in message:
                self.importantIndexes.registration_complete_index = i
                self.importantIndexes.registration_complete_time = timeIot

    def saveToCsv(self, name):
        all_lists = [self.frame, self.slot, self.info, self.layer, self.direction, self.message, self.extrainfo, self.timeIot]
        csv_file_path = "output" + str(name) + ".csv"

        # Define the number of rows to save
        num_rows_to_save = 3000

        # Open the CSV file in write mode
        with open(csv_file_path, mode='w', newline='') as file:
            # Create a CSV writer object
            writer = csv.writer(file)
            
            # Write the first num_rows_to_save rows from the lists to the CSV file
            for i, row in enumerate(zip(*all_lists)):
                if i >= num_rows_to_save:
                    break
                writer.writerow(row)

    def getPuschTimes(self, lim):
        for i, (info, layer) in enumerate(zip(self.info, self.layer)):
            if Layer.PHY == layer:
                if Channel.PUSCH.value in info:
                    #if self.timeIot[i] > self.importantIndexes.registration_complete_time and self.timeIot[i] < 10:
                    if self.timeIot[i] < lim:
                        self.importantIndexes.pusch_times.append(self.timeIot[i])

    def getPdcchTimes(self, lim):
        for i, (info, layer) in enumerate(zip(self.info, self.layer)):
            if Layer.PHY == layer:
                if Channel.PDCCH.value in info:
                    #if self.timeIot[i] > self.importantIndexes.registration_complete_time and self.timeIot[i] < 10:
                    if self.timeIot[i] > -0.5 and self.timeIot[i] < lim:
                        self.importantIndexes.pdcch_times.append(self.timeIot[i])

    def getPdschTimes(self, lim):
        for i, (info, layer) in enumerate(zip(self.info, self.layer)):
            if Layer.PHY == layer:
                if Channel.PDSCH.value in info:
                    #if self.timeIot[i] > self.importantIndexes.registration_complete_time and self.timeIot[i] < 10:
                    if self.timeIot[i] < lim:
                        self.importantIndexes.pdsch_times.append(self.timeIot[i])

    def getPucchTimes(self):
        aux = []
        for i, (info, layer) in enumerate(zip(self.info, self.layer)):
            if Layer.PHY == layer:
                if Channel.PUCCH.value in info:
                    #if self.timeIot[i] > self.importantIndexes.registration_complete_time and self.timeIot[i] < 10:
                    if self.timeIot[i] > 0 and self.timeIot[i] < 10:
                        aux.append(self.timeIot[i])
        return aux

    def getPowerOfPhysicalTransmission(self, index, psu_times, psu_powers):

        time_transmission = self.timeIot[index]
        time_transmission_end = time_transmission + 0.0005

        mask = (psu_times > time_transmission) & (psu_times < time_transmission_end)
        relevant_powers = psu_powers[mask]

        if len(relevant_powers) == 0:
            # print("No powers found within the specified time range") #Means we are at the end, and beyond
            return -1
        
        # doubled_powers = self.double_points_by_average(relevant_powers)
        
        return np.mean(relevant_powers)
    
    def getAllPuschPowers(self, psu_logs):
        psu_times = np.array([psu_log.time_psu for psu_log in psu_logs.psu_logs])
        psu_powers = np.array([psu_log.power for psu_log in psu_logs.psu_logs])
        
        for i, (info, layer) in enumerate(zip(self.info[self.importantIndexes.registration_complete_index:], self.layer[self.importantIndexes.registration_complete_index:]), start=self.importantIndexes.registration_complete_index):
            if Layer.PHY == layer:
                if Channel.PUSCH.value in info:

                    power = self.getPowerOfPhysicalTransmission(i, psu_times, psu_powers)
                    if power == -1 and i > self.importantIndexes.registration_complete_index + 2:
                        break
                    self.powers.append(power)
    
    def getAllPdschPowers(self, psu_logs):
        psu_times = np.array([psu_log.time_psu for psu_log in psu_logs.psu_logs])
        psu_powers = np.array([psu_log.power for psu_log in psu_logs.psu_logs])
        
        for i, (info, layer) in enumerate(zip(self.info[self.importantIndexes.registration_complete_index:], self.layer[self.importantIndexes.registration_complete_index:]), start=self.importantIndexes.registration_complete_index):
            if Layer.PHY == layer:
                if Channel.PDSCH.value in info:

                    power = self.getPowerOfPhysicalTransmission(i, psu_times, psu_powers)
                    if power == -1:
                        break
                    self.powers_pdsch.append(power)

    def getMeanAndDeviationPusch(self):

        self.p_tx_mean = np.mean(self.powers)
        self.p_tx_min = min(self.powers)
        self.p_tx_max = max(self.powers)
        self.p_tx_standard_deviation = np.std(self.powers)
        self.p_tx_median = np.median(self.powers)
        self.p_tx_confidence_interval = stats.norm.interval(0.95, loc=self.p_tx_mean, scale=stats.sem(self.powers))

        print("Mean and Deviation Calculated")
    
    def getMeanAndDeviationPdsch(self):

        self.p_rx_mean = np.mean(self.powers_pdsch)
        self.p_rx_min = min(self.powers_pdsch)
        self.p_rx_max = max(self.powers_pdsch)
        self.p_rx_standard_deviation = np.std(self.powers_pdsch)
        self.p_rx_median = np.median(self.powers_pdsch)
        self.p_rx_confidence_interval = stats.norm.interval(0.95, loc=self.p_rx_mean, scale=stats.sem(self.powers_pdsch))

        print("Mean and Deviation Calculated")

    def saveDataForTrainingPusch(self):
        with open(os.path.join('DeepLearning','tx', 'data' + '.csv'), 'a', newline='') as file:
            writer = csv.writer(file)
            
            for power in self.powers:
                writer.writerows([
                    [self.p_max, mcs_table_conversion[f'{self.mcs_table}_{self.mcs_index}'], self.mimo, power,]
                ])

    def saveDataForTrainingPdsch(self):
        with open(os.path.join('DeepLearning','rx', 'data' + '.csv'), 'a', newline='') as file:
            writer = csv.writer(file)
            
            for power in self.powers_pdsch:
                writer.writerows([
                    mcs_table_conversion[f'{self.mcs_table}_{self.mcs_index}'],
                    self.mimo,
                    power,
                ])

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
    
    def __init__(self, prach_index=None):

        self.prach_index = prach_index
        self.prach_time = 0

        self.registration_complete_index = 0
        self.registration_complete_time = 0

        self.pusch_times = []
        self.pdcch_times = []
        self.pdsch_times = []

    def getAllTimesList(self):
        return [[self.prach_time], [self.registration_complete_time], self.pusch_times, self.pdcch_times]
        