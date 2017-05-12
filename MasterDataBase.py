import time
import sqlite3
import serial
import string
import random

# Database Globals
dataBase = sqlite.connect('PaccarConnect.db')
cursor = conn.cursor()

# Globals Variables
sensorCount = 0

def createSensorList():

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Sensor_List(
        sensorID INTEGER,
        sensorType TEXT
        )''')
    dataBase.commit()
    cursur.close()
    dataBase.close()
    
    #End createTable()

def createDataLog():

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Data_Log(
        sensorID INTEGER,
        sensorType TEXT,
        data INTEGER,
        timeOfLog TEXT,
        date TEXT,
        severity INTEGER
        )''')
    dataBase.commit()
    cursur.close()
    dataBase.close()
    
    #End createDataLog()
    

def addSensorToList(sensorID, sensorType):

    cursor.execute("INSERT INTO Sensor_List (sensorID, sensorType) VALUES (?,?)",
                   (sensorID, sensorType))
    dataBase.commit()
    sensorCount += 1

    #End addSensorToLIst()

def enterDataLogEntry(sensorID, sensorType, data, timeOfLog, date, severity):

    cursor.execute("INSERT INTO Data_Log (sensorID, sensorType, data, timeOfLog, date, severity) VALUES (?,?,?,?,?,?)",
                   (sensorID, sensorType, data, timeOfLog, date, severity))
    dataBase.commit()

    #End enterDataLogEntry()

def createInOutQueue():

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS inQueue(
        messageID INTEGER,
        functionName TEXT,
        messageArrivalTime TEXT,
        )''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS outQueue(
        messageID INTEGER,
        functionName TEXT,
        messageArrivalTime TEXT
        )''') 

    dataBase.commit()
    cursur.close()
    dataBase.close()

    #End createInOutQueue()

# Helper Functions

def writeToQueueOut(messageID):

    timeOfLog = datetime.datetime.now().time()
    cursor.execute("INSERT INTO outQueue (messageID, fuctionName, messageArrivalTime) VALUES (?,?,?)",
                   (messageID, getFunctionName(messageID), timeOfLog))
    cursor.commit()

def getFunctionName(messageID):

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

def process(messageID):

    cursor.execute('SELECT * FROM inQueue where messageID = ?', (messageID,))
    

    

    


    
    

    


    
