import mysql.connector
import queries



def connectToDb():
    myDb = mysql.connector.connect(user='admin', password='alliot',
        host='alliot-kontrondev.alb.is.keysight.com',
        database='postgres')

    cursor = myDb.cursor()

    cursor.close()
    myDb.close()
    print("Hello World")

def myMain():
    print(queries.iot_query)

if __name__ == "__main__":
    myMain()