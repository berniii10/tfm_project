import os, glob
import pandas as pd
from psycopg2 import Error
from database.DbConnection import *

class CampaignPsuLogs:

    def __init__(self):
        self.campaign_psu_logs = []

    def howManyTestPlans(self):
        return len(self.psu_logs)
    
    def loadData(self, rows, sweeps=None):
        indexes = {}
        temp_psu_logs = {}

        for i, row in enumerate(rows):

            resulttypeid = int(row[0])
            if resulttypeid in indexes:
                indexes[resulttypeid] += 1

            else:
                indexes[resulttypeid] = 0

            if resulttypeid in temp_psu_logs:
                temp_psu_logs[resulttypeid].append(PsuLog(*row))
            else:
                temp_psu_logs[resulttypeid] = []
        
        if sweeps == None:
            self.campaign_psu_logs  = [PsuLogs() for i in range(len(temp_psu_logs))]

            for i, key in enumerate(temp_psu_logs):
                self.campaign_psu_logs[i].loadPsuData(temp_psu_logs[key])
        else:
            self.campaign_psu_logs  = [PsuLogs()]

            self.campaign_psu_logs[0].loadPsuData(temp_psu_logs[next(iter(temp_psu_logs))])
        
        return 1
    
    def loadDataFromCsv(self, pmax, mcs_table, mcs_index, n_antenna_ul, n_antenna_dl):
        for n_antenna_ul, n_antenna_dl in zip(n_antenna_ul, n_antenna_dl):
                for mcs_table in mcs_table:
                    for mcs_index in mcs_index:
                        for pmax in pmax:

                            temp_psu_logs = []

                            matching_files = glob.glob(os.path.join('datastructures','files', 'CampaignOutput', f'TX_PSU_pmax{pmax}_MCS{mcs_table}-{mcs_index}_UL{n_antenna_ul}_DL{n_antenna_dl}*' + '.csv'))
                            if matching_files:
                                if len(self.campaign_psu_logs) > 0:
                                    self.campaign_psu_logs.append(PsuLogs())
                                else:
                                    self.campaign_psu_logs = [PsuLogs()]

                                df = pd.read_csv(matching_files[0])
                                for i, row in df.iterrows():
                                    temp_psu_logs.append(PsuLog(1, row['Start Time'], row['Amperes'], row['Volts'], row['Origin']))

                                self.campaign_psu_logs[len(self.campaign_psu_logs)-1].loadPsuData(temp_psu_logs)
                            else: 
                                print("No matching files found for: " + os.path.join('datastructures','files', 'CampaignOutput', f'TX_PSU_pmax{pmax}_MCS{mcs_table}-{mcs_index}_UL{n_antenna_ul}_DL{n_antenna_dl}*' + '.csv'))
                                return -1


    def searchVoltageSpike(self):
        for campaign_psu_log in self.campaign_psu_logs:
            if campaign_psu_log.searchVoltageSpike() == -1:
                return -1

    def calculateTimePsuAndPower(self):
        for campaign_psu_log in self.campaign_psu_logs:
            campaign_psu_log.calculateTimePsuAndPower()

    def findTwoMaxValues(self):
        for campaign_psu_log in self.campaign_psu_logs:
            campaign_psu_log.findTwoMaxValues()

class PsuLogs:
    
    def __init__(self):
        self.psu_time_offset = 0
        self.voltage = 5
        self.psu_logs = []

    def addPsuLog(self, psu_log):
        self.psu_logs.append(psu_log)

    def loadPsuData(self, psu_logs):
        for psu_log in psu_logs:
            self.addPsuLog(psu_log)

        print("Psu Data loaded correctly")
        return 1

    def searchVoltageSpike(self):
        found = -1
        for i, psu_log in enumerate(self.psu_logs):
            # if psu_log.amperes > 0.3: #0.275:
            if psu_log.volts > 1.5: #0.275:
                self.psu_time_offset = psu_log.starttime
                print(f"Voltage Spike found at time {self.psu_time_offset} and index {i}")
                found = 1
                break
            
        return found

    def calculateTimePsuAndPower(self):
        for psu_log in self.psu_logs:
            psu_log.time_psu = psu_log.starttime - self.psu_time_offset
            psu_log.power = self.voltage * psu_log.amperes

    def findTwoMaxValues(self):
        max1 = 0.0
        max2 = 0.0
        for psu_log in self.psu_logs:
            if psu_log.volts > max1:
                max1 = psu_log.volts
                max2 = max1
            elif max2 > psu_log.volts:
                max2 = psu_log.volts

        print(f"Result Type ID: {self.psu_logs[0].resulttypeid} Maximum: {max1} and Maximum2: {max2}")

class PsuLog:

    def __init__(self, resulttypeid, starttime, amperes, volts, origin):
        self.resulttypeid = int(resulttypeid)
        self.starttime = float(starttime)
        self.amperes = float(amperes)
        self.volts = float(volts)
        self.origin = float(origin)

        time_psu = 0
        power = 0
