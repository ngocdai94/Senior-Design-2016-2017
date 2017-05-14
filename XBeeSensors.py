# Keoni Akina
# ECE Team 17.6
# This Script functions only to take in Zigbee data and log it in the
# DataBase
# Todo compile a shell script including this script and master server and populate database


from xbee import XBee, DigiMesh, ZigBee
import time
import datetime
import sqlite3
import serial
import string
import random

# Database Globals
dataBase = sqlite3.connect('PaccarConnect.db')
cursor = dataBase.cursor()

SERIALPORT = "/dev/ttyUSB0"    # the com/serial port the XBee is connected to, the pi GPIO should always be ttyAMA0
BAUDRATE = 9600            # Baudrate used to communicate over serial
door = '\x00\x13\xa2\x00@\xe56\x8f'
analog = '\x00\x13\xa2\x00@\xe8\x98\xae'
date = time.strftime("%y/%m/%d")
TEMP = 'Temperature'
HUMID = 'Humidity'
DOORSTAT = 'Door Status'

ser = serial.Serial(SERIALPORT, BAUDRATE, timeout = 1)
xBee = ZigBee(ser)

macTempHumid = "MAC_ADDR:TEMP:HUMID:DUMMY"
doorMacAddr = '0013a20040e5368f' 

#Sensor ID Globals
doorSensorID = 1

# MAC Address for Senors
doorMacAddr = '0013a20040e5368f'

# Sensor Type Globals
doorSensorType = "Door_Sensor"

def enterDataLogEntry(sensorID, sensorType, data, timeOfLog, severity):

    cursor.execute('''INSERT INTO Data_Log
        (sensorID, sensorType, data, timeOfLog, severity)
        VALUES (?,?,?,?,?)''',
        (sensorID, sensorType, data, timeOfLog, severity))
    dataBase.commit()

    #end enterDataLogEntry()

def insertDoorData(data):
    
    global doorSensorID
    global doorSensorType
    timeOfLog = str(datetime.datetime.now().time())[0:8]
    severity = 0
    if (data == True):
        severity = 1
        dataEntry = 1
    else:
        dataEntry = 0

    enterDataLogEntry(doorSensorID, doorSensorType,
                      dataEntry, timeOfLog, severity)

    
    #end insertDoor()

def getDoorSensorData():
    
    global doorMacAddr

    response = getXbeeResponse()
    addr = response['source_addr_long'].encode('hex')
 
    if (addr == doorMacAddr):
        data = response['samples']
        readings = []
        for item in data:
            readings.append(item.get('dio-0'))
            return (int(readings[0]))

    #end getDoorSensorData()
        
        

def getXbeeResponse():

    global xBee
    return xBee.wait_read_frame()

    #end getXbeeResponse()

def main():

    print("Gathering Data")
    while True:
        try:
            data = getDoorSensorData()
            insertDoorData(data)
            time.sleep(.5)
        except KeyboardInterrupt:
            cursor.close()
            dataBase.close()
##        data = getXbeeResponse()['samples']
##        readings = []
##        for item in data:
##            readings.append(item.get('dio-0'))
##        #print(readings[0])
##        insertDoorData(int(readings[0]))
        
    cursor.close()
    dataBase.close()

    #end main()

main()
    






    
    
