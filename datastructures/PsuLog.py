from psycopg2 import Error
from database.DbConnection import *
class PsuLogs:
    
    psu_time_offset = 0
    voltage = 5
    psu_logs = []

    def __init__(self):
        pass

    def addPsuLog(self, psu_log):
        self.psu_logs.append(psu_log)

    def loadPsuData(self, myDb, campaignId):
        print("Loading PSU Data")
        try:
            cursor = myDb.cursor()

            cursor.execute(getPsuQuery(campaignId))
            rows = cursor.fetchall()

            # Process the result set and create instances of PsuLog class
            for row in rows:
                self.addPsuLog(PsuLog(*row))

            # Close the cursor and connection
            cursor.close()

            print("PSU Data loaded correctly")
            return 1

        except Error as e:
            print(f"Error: {e}")
            return -1

    def searchVoltageSPike(self):
        found = -1
        for psu_log in self.psu_logs:
            if psu_log.volts > 1:
                self.psu_time_offset = psu_log.starttime
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

        print(f"Maximum: {max1} and Maximum2: {max2}")

class PsuLog:
    
    time_psu = 0
    power = 0

    def __init__(self, resulttypeid, starttime, amperes, volts, origin):
        self.resulttypeid = int(resulttypeid)
        self.starttime = float(starttime)
        self.amperes = float(amperes)
        self.volts = float(volts)
        self.origin = float(origin)
