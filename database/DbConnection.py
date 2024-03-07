import psycopg2

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

def closeConnection(myDb):
    myDb.close()