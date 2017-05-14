import time
import sqlite3
import serial
import string
import random
import datetime

# Database Globals
dataBase = sqlite3.connect('PaccarConnect.db')
cursor = dataBase.cursor()

# Globals Variables
sensorCount = 0

#ProfileID Globals
perishables = 1
nonPerishables = 2
frozen = 3
electronics = 4
furniture = 5
misc = 6

#SensorID Numbers
doorSensorID = 1
tempSensorID = 2

def createSensorList():

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Sensor_List(
        sensorID INTEGER,
        sensorType TEXT
        )''')
    dataBase.commit()
    
    #End createTable()

def createDataLog():

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Data_Log(
        sensorID INTEGER,
        sensorType TEXT,
        data INTEGER,
        timeOfLog TEXT,
        severity INTEGER
        )''')
    dataBase.commit()
    
    #End createDataLog()
    

def addSensorToList(sensorID, sensorType):

    cursor.execute("INSERT INTO Sensor_List (sensorID, sensorType) VALUES (?,?)",
                   (sensorID, sensorType))
    dataBase.commit()
    sensorCount += 1

    #End addSensorToLIst()


def createInOutQueue():

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS inQueue(
        messageID INTEGER,
        functionName TEXT,
        messageArrivalTime TEXT
        )''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS outQueue(
        profileName TEXT,
        sensorName TEXT,
        data INTEGER
        )''') 

    dataBase.commit()

    #End createInOutQueue()



def writeToQueueOut(profileID,sensorNum,data):

    cursor.execute('''INSERT INTO outQueue
        (profileName, sensorName, data) VALUES (?,?,?)''',
        (getProfileName(profileID), getSensorName(sensorNum), data))
    dataBase.commit()

    #End writeToQueueOut

def getFunctionName(messageID): # Helper Functions

    if ((messageID < 0) or (messageID > 10)):
        return 'Invalid_Message_Id'

    if (messageID == 1):
        return 'get_sensor_data'
    elif (messageID == 2):
        return 'get_profile_list'
    elif (messageID == 3):
        return 'get_sensor_list'
    elif (messageID == 4):
        return 'get_notification_count'
    elif (messageID == 5):
        return 'get_notifications'
    elif (messageID == 6):
        return 'is_connected'
    elif (messageID == 7):
        return 'create_profile'
    elif (messageID == 8):
        return 'get_history'
    elif (messageID == 9):
        return 'get_sensor_config_data'
    else:
        return 'save_sensor_config_data'

    #End getFunctionName()

def readInQueue():

    array = []
    for row in cursor.execute('''SELECT * FROM inQueue where rowid = 1'''):
        array.append(row)
        return array

    #End readInQueue()

def getInQueueCommand(messageID):

    if (messageID == 1):
        cursor.execute('''SELECT * FROM inQueue where rowid = 1''')
        for doc in cursor:
            data = doc
            if (True):
                return data
    else:
        return -1
        

def getProfileName(profileID):

    if ((profileID < 1) or (profileID > 6)):
        return 'INVALID PROFILE ENTRY'
    
    if (profileID == 1):
        return 'Perishables'
    elif (profileID == 2):
        return 'Non-Perishables'
    elif (profileID == 3):
        return 'Frozen'
    elif (profileID == 4):
        return 'Electronics'
    elif (profileID == 5):
        return 'Furniture'
    elif (profileID == 6):
        return 'Miscellaneous'
    else:
        return 'INVALID PROFILE ENTRY'

    #End getProfileID

def getSensorName(sensorID):

    if ((sensorID < 1) or (sensorID > 2)):
        return 'INVALID DOOR SENSOR'
    if (sensorID == 1):
        return 'DoorSensor_1'

    

### These are testing functions not to be used in the full script  ###

def writeToQueueIn(messageID):

    timeOfLog = str(datetime.datetime.now().time())[0:8]
    cursor.execute('''INSERT INTO inQueue
        (messageID, functionName, messageArrivalTime) VALUES (?,?,?)''',
        (messageID, getFunctionName(messageID), str(timeOfLog)))
    dataBase.commit()

    #End writeToQueueOut
    
def readOutQueue():

    cursor.execute('SELECT * FROM outQueue where rowid = 1')
    for doc in cursor:
        print(doc)

    #End readInQueue()

def enterDataLogEntry(sensorID, sensorType, data, timeOfLog, date, severity):

    cursor.execute('''INSERT INTO Data_Log
        (sensorID, sensorType, data, timeOfLog, severity)
        VALUES (?,?,?,?,?,?)''',
        (sensorID, sensorType, data, timeOfLog, severity))
    dataBase.commit()

    #End enterDataLogEntry()

### TESTING FUNCTIONS::TESTING FUNCTIONS:: TESTING FUNCTIONS  ###

    

def main():

    print('Setting up Database...')
##    time = str(datetime.datetime.now().time())
##    print(time[0:8])

    createDataLog()
    createInOutQueue()

    while True:
        raw_input("Press Enter After BluetoothScript runs...")
        try:
            profileName = readInQueue()
            print(profileName)
            print(type(profileName))
            print(profileName[0])
            #print("profileName: " + profileName + " Type: ")
            #print(type(profileName))
            raw_input("Press Enter, yo...")
            writeToQueueOut(profileName[0],profileName[1],1313133)

        except KeyboardInterrupt:
            cursor.close()
            dataBase.close()

main()

    

    
    

    


    
    

    


    
