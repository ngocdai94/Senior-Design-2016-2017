import time
import sqlite3
import serial
import string
import random
import datetime
import json

from string import maketrans

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

def createNotificationList():

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS notificationList(
        id INTEGER PRIMARY KEY,
        uid INTEGER,
        type TEXT,
        value REAL,
        times REAL)''')
    dataBase.commit()

    #End createNotificationList()

def createConfigList():

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS configList(
        id INTEGER PRIMARY KEY,
        profileID INTEGER,
        sensorID INTEGER,
        sensorType TEXT,
        lowerThreshold REAL,
        upperThreshold REAL,
        severity TEXT,
        state INTEGER,
        interval REAL)''')
    dataBase.commit()

    #End createConfigList()

def createProfileList():

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS profileList(
        id INTEGER PRIMARY KEY,
        profileID INTEGER,
        profileName TEXT,
        profileType TEXT,
        active INTEGER)''')
    dataBase.commit()

    createProfile(1,'Perishables','Default',0)
    createProfile(2,'Non-Perishables','Default',0)
    createProfile(3,'Frozen','Default',0)
    createProfile(4,'Electronics','Default',0)
    createProfile(5,'Furniture','Default',0)
    createProfile(6,'MISC','Default',0)

    dataBase.commit()

    #End createProfileList()

def createProfile(profileID, profileName, profileType, active):
    cursor.execute('''
        INSERT INTO profileList(profileID, profileName, profileType, active)
        VALUES(?,?,?,?)''', (profileID, profileName, profileType, active))
    dataBase.commit()

    #End createProfile()

##compares processed data to threhold values to determine errors
def severityCheck(sensorProcessed, sensorType, sensorID, profileID):

    if sensorType == "BINARY":
        cursor.execute('''SELECT state FROM configList WHERE profileID = ? AND sensorID = ?''',(profileID, sensorID))
        state = cursor.fetchone()
        if sensorProcessed == state[0]:
            return False
        else:
            print("error detected")
            return True
    else:
        cursor.execute('''SELECT upperThreshold FROM configList WHERE profileID = ? AND sensorID = ?''',(profileID, sensorID))
        tU = cursor.fetchone()
        cursor.execute('''SELECT lowerThreshold FROM configList WHERE profileID = ? AND sensorID = ?''',(profileID, sensorID))
        tL = cursor.fetchone()
        if sensorProcessed > tU[0] or sensorProcessed < tL[0]:
            print("error detected")
            return False
        else:
            return True

        #End severityCheck()

def configListDefaults(profileID, sensorID, sensorType, lowerThresh, upperThresh):

    cursor.execute('''
        INSERT INTO configList(profileID, sensorID, sensorType, lowerThreshold, upperThreshold, severity, state, interval)
        VALUES(?,?,?,?,?,?,?,?)''', (profileID, sensorID, sensorType, lowerThresh, upperThresh, 'LOW', 0, 10))
    dataBase.commit()

    #End configlistDefaults()


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
        jsonData TEXT,
        messageArrivalTime TEXT,
        jobProcessed INTEGER
        )''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS outQueue(
        messageID INTEGER,
        jsonData TEXT,
        messageSentTime INTEGER,
        jobProcessed INTEGER
        )''') 

    dataBase.commit()

    #End createInOutQueue()

def createDataBuffer():
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS dataBuffer(
        id INTEGER PRIMARY KEY,
        sensorID INTEGER,
        sensorType TEXT,
        value REAL,
        times REAL)''')
    dataBase.commit()

    #End createDataBuffer()


def writeToQueueOut(messageID,jsonData):
        

    jobProcessed = False
    timeOfLog = str(datetime.datetime.now().time())[0:8]
    cursor.execute('''INSERT INTO outQueue
        (messageID, jsonData, messageSentTime, jobProcessed) VALUES (?,?,?,?)''',
        (messageID, jsonData, timeOfLog, int(jobProcessed)))
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

    print ("readInQueue() called...")
    inQueueMessage = []
    #for row in cursor.execute('''SELECT * FROM inQueue where rowid = 1'''):
    for row in cursor.execute('''SELECT * FROM inQueue WHERE jobProcessed = 0 LIMIT 1'''):
        inQueueMessage.append(row)
        break

    return inQueueMessage

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

    if (sensorID == 666):
        return 'INITIAL VALUE'

    if ((sensorID < 1) or (sensorID > 2)):
        return 'INVALID DOOR SENSOR'
    if (sensorID == 1):
        return 'DoorSensor_1'

    

### These are testing functions not to be used in the full script  ###

def writeToQueueIn(messageId, jsonData):
    
    jobProcessed = False
    if (messageId == 666):
        jobProcessed = True
    timeOfLog = str(datetime.datetime.now().time())[0:8]
    cursor.execute('''INSERT INTO inQueue
        (messageID, jsonData, messageArrivalTime, jobProcessed) VALUES (?,?,?,?)''',
        (messageId, jsonData, str(timeOfLog), int(jobProcessed)))
    dataBase.commit()
    
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

def parseProfileName(profileName):

    parsedProfile = profileName.replace("(","")
    parsedProfile = parsedProfile.replace(",","")
    parsedProfile = parsedProfile.replace("u","")
    parsedProfile = parsedProfile.replace("'","")
    parsedProfile = parsedProfile.replace(")","")

    array = parsedProfile.split()

    return array

    #End parseProfileName()

def dropAllTables():

    cursor.execute('drop table if exists inQueue')
    cursor.execute('drop table if exists outQueue')
    cursor.execute('drop table if exists Data_Log')
    cursor.execute('drop table if exists btisConnected')

def createCallbackTable():

        cursor.execute('''
        CREATE TABLE IF NOT EXISTS btIsConnected(
        isConnected INTEGER
        )''') 

        isConnected = 0
        cursor.execute('''INSERT INTO btIsConnected VALUES (?)''',
                       (isConnected,))
        dataBase.commit()

def verifyBTConnection():

    for isConnected in cursor.execute('SELECT * FROM btIsConnected LIMIT 1'):
        True
        
    return(bool(isConnected[0]))

    #End verifyBTConnection()
    

def verifyInQueueContent():

    jobToProcessExists = False
    for jobProcessed in cursor.execute('SELECT * FROM inQueue where jobProcessed = 0 LIMIT 1'):
        jobToProcessExists = True
        break
        
    return (jobToProcessExists)

def setBTConnection(setConnection):

    if setConnection:
        cursor.execute('UPDATE btIsConnected SET isConnected = 1 LIMIT 1')
        dataBase.commit()
        return True
    else:
        cursor.execute('UPDATE btIsConnected SET isConnected = 0 LIMIT 1')
        dataBase.commit()
        return False

    #End setBTConnection

def updateInQueueTableProcess():

    cursor.execute('UPDATE inQueue SET jobProcessed = 1 WHERE jobProcessed = 0 Limit 1')
    dataBase.commit()

    #End setBTConnection

##This function takes the sensorData in chunks of any size and returns processed data by avg
def dataAveraging(sensorData, sensorType):
    trues = 0
    falses = 0
    if len(sensorData) > 0:
        if sensorType == "BINARY":
            for elements in sensorData:
                if elements == True:
                    trues = trues + 1
                else:
                    falses = falses + 1
                if trues > falses or trues == falses:
                    return 1
                else:
                    return 0
        else:        
            return sum(sensorData)/len(sensorData)
    else:
        return 0

    #End dataAveraging()

##This method pulls data from the data buffer
def dataBufferQuery(sensorID):

    cursor.execute('''SELECT value FROM dataBuffer WHERE sensorID = ?''', (sensorID,))
    sensorData = cursor.fetchall()
    dataBase.commit()
    data = [i[0] for i in sensorData]
    return data

    #end dataBufferQuery()

def profileTableQuery():

    cursor.execute('''SELECT profileID FROM profileList WHERE active = 1''')
    profileID = cursor.fetchone()
    dataBase.commit()
    print("ActiveProfile: " + str(profileID))

    #End ProfileID

def setProfileIsActive(profileID): # 1st param is ID to turnOff 2nd is param to turnOn

    cursor.execute('UPDATE profileList SET active = 0 WHERE active = 1')
    dataBase.commit()

    cursor.execute('''UPDATE profileList SET active = 1 WHERE profileID = ?''',(profileID,))
    dataBase.commit()

    #End setBTConnection
    

def processDataBufferTest(sensorID):

    sensorType = getSensorType(sensorID)
    sensorData = dataBufferQuery(sensorID)
    profileID = sensorID # This needs to be more dynamic, yo!
    sensorAverage = dataAveraging(sensorData, sensorType)
    errors = severityCheck(sensorAverage, sensorType, sensorID,sensorID)

def getSensorType(sensorID):

    if (sensorID == 1):
        return "Non-BINARY"
    else:
        return "BINARY"

def getProfileList():
    
    cursor.execute('''SELECT profileID, profileName, profileType, active FROM profileList''')
    profiles = cursor.fetchall()
    #profiles = ''.join(str(e) for e in profiles)
    #profiles = parseProfileName(profiles)

    dataNode = []
    for profile in profiles:
        dataRow = {}
        dataRow['profileID'] = profile[0]
        dataRow['profileName'] = profile[1]
        dataRow['profileType'] = profile[2]
        dataRow['active'] = profile[3]
        dataNode.append(dataRow)

    parentJsonNode = {"messageID: 2": dataNode}
    message = json.dumps(parentJsonNode)                
    return message

def main():

    print('Setting up Database...')

    #dropAllTables()
##    createDataLog()
##    createInOutQueue()
##    createCallbackTable()
##    createNotificationList()
##    createConfigList()
##    createProfileList()
##    verifyInQueueContent()
##    createDataBuffer()

    # Testing   
    #setProfileIsActive(4)
    #profileTableQuery()
    #getProfileList()

    profileID = 999
    sensorID = 888
    sensorType = 777
    lowerThresh = 444
    upperThresh = 555

    # Set defaults for configuration lists
    configListDefaults(1, 1, 'BINARY', 0,1) #Door Sensor
    configListDefaults(2,2,'Analog',22,27) #Temperature

    
    #writeToQueueOut(666,666)
    #writeToQueueIn(2, 666)
    
    print("Waiting for Bluetooth Connection...")

    #setBTConnection(True)

    while not verifyBTConnection():
        True

    print("Bluetooth Connected")
        

    while True:

            
        while not verifyBTConnection(): #wait for connection
            time.sleep(2)
            
        try:
            if (verifyInQueueContent()):
                message = ''.join(str(e) for e in readInQueue())
                #raw_input("Before Update inQueueTable")
                message = parseProfileName(message)
                print(message)
                print(message[0])
                if (int(message[0]) == 2):
                    jsonData = getProfileList()
                    writeToQueueOut(2,jsonData)
                updateInQueueTableProcess()
                #raw_input("After Update inQueueTable")
                

        except KeyboardInterrupt:
            cursor.close()
            dataBase.close()
            setBTConnection(False)
            print(str(datetime.datetime.now().time())[0:8])

main()
