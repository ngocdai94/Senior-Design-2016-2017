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
    

    
