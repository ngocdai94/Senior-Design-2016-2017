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

##SERIALPORT = "/dev/ttyUSB0"    # the com/serial port the XBee is connected to, the pi GPIO should always be ttyAMA0
##BAUDRATE = 9600            # Baudrate used to communicate over serial
##door = '\x00\x13\xa2\x00@\xe56\x8f'
##analog = '\x00\x13\xa2\x00@\xe8\x98\xae'
##date = time.strftime("%y/%m/%d")
##TEMP = 'Temperature'
##HUMID = 'Humidity'
##DOORSTAT = 'Door Status'

##ser = serial.Serial(SERIALPORT, BAUDRATE, timeout = 1)
##xBee = ZigBee(ser)


#Sensor ID Globals
doorSensorID = 1
humidTempID = 2

# MAC Address for Senors
doorMacAddr = '0013a20040e5368f'
#macTempHumid = '0013a20040e53397'
macTempHumid = '0013a20040e53693'

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

    data = str(data)
    timeOfLog = str(datetime.datetime.now().time())[0:8]
    severity = 0 #TODO scale this later
    
    if (data == '[True]'):
        severity = 1
        dataEntry = 1
    else:
        dataEntry = 0

    enterDataLogEntry(doorSensorID, doorSensorType,
                      dataEntry, timeOfLog, severity)
    writeToDataBuffer(doorSensorID, 'BINARY',dataEntry)
        
    #end insertDoor()

##def insertHumidTemp(data):
##
##    global humidTempID
##
##    lowThresh = 65
##    upThresh = 85
##    severity = 1
##    if (data < lowThresh or data > upThresh):
##        serverity = 10
##    
##    timeOfLog = str(datetime.datetime.now().time())[0:8]
##    enterDataLogEntry(humidTempID, 'Temperature',
##                      data, timeOfLog, severity)
##    writeToDataBuffer(humidTempID , 'NON-BINARY', data)
##
##

    #end insertHumidTemp()
    

def getDoorSensorData(response):
    
    data = response['samples']
    readings = []
    for item in data:
        readings.append(item.get('dio-0'))
    return readings

    #end getDoorSensorData()

def getTempHumid(response):

    data = response['samples']
    readings = []

    for item in data:
        readings.append(item.get('adc-0'))
        readings.append(item.get('adc-1'))

    return readings[0] # return temperature value

##def getTempHumid(data):
##
##    global macT
##    print("getTempHumid() runnning...")
##    response = getXbeeResponse()
##    addr = response['source_addr_long'].encode('hex')
##    print(addr) 
##    if (addr == '0013a20040e53693'): #macTempHumid):
##        data = response['samples']
##        print(data)
##        readings = []
##        for item in data:
##            readings.append(item.get('dio-0'))
##        print readings
##
##    #end getTempHumid()


#data (type list) in this function has 2 items
#1 is temperature, and 1 is hudmidlity
def insertHumidTemp(data):

    tempSensorType = 'Temperature'
    
    dataEntry = (120*data/1023-40)*1.8+32
    #print (dataEntry)
    timeOfLog = str(datetime.datetime.now().time())[0:8]
    severity = 0
    
    # TODO write database query to check thresholds
    
    enterDataLogEntry(humidTempID, tempSensorType,
                      dataEntry, timeOfLog, severity)
    writeToDataBuffer(humidTempID , 'NON-BINARY', dataEntry)

    dataBase.commit()
    
    #end insertHumidTemp


def tempHumidTest():
    #receive message

    response = getXbeeResponse()
    print(response)
    if response['rf_data']:
        readings = response['rf_data'].split()
        #print(readings[0])
        

def getXbeeResponse():

    global xBee
    return xBee.wait_read_frame()

    #end getXbeeResponse()

def writeToDataBuffer(sensorID, sensorType, value):

    timeOfLog = str(datetime.datetime.now().time())[0:8]
    cursor.execute('''
        INSERT INTO dataBuffer(sensorID, sensorType, value, times)
        VALUES(?,?,?,?)''', (int(sensorID),str(sensorType), value, timeOfLog))
    dataBase.commit()

    #End writeToDataBuffer()

def main():
    print("Gathering Data")
    while True:
        #the reponse and addr are taken down from
        #getTempHumid and getDoorSensorData functions
        response = getXbeeResponse()
        if (response):
            addr = response['source_addr_long'].encode('hex')
        try:
            # check if see temp sensor?, otherwise go to door sensor
##            if (addr == doorMacAddr):
##                data = getDoorSensorData(response)
##                print("door Data: " + str(data))
##                insertDoorData(data)
##                    
##            else:             
##                #data = getTempHumid(response)
##                #print("temp data: " + str(data))
##                #if data > 200:
##                 #   insertHumidTemp(data)
            insertDoorData(random.randint(0,1))
            insertHumidTemp(random.randint(60,90))

            time.sleep(.5)

        except KeyboardInterrupt:
            cursor.close()
            dataBase.close()

    cursor.close()
    dataBase.close()

    #end main()

main()


##def main():
##
##    print("Gathering Data")
##    while True:
##        try:
##            #response = getDoorSensorData()
##            insertDoorData(random.randint(0,1))
##            insertHumidTemp(random.randint(60,90))
##            time.sleep(1)
##        except KeyboardInterrupt:
##            cursor.close()
##            dataBase.close()        
##    cursor.close()
##    dataBase.close()
##    print(str(datetime.datetime.now().time())[0:8])
##
##    #end main()
##
##main()

