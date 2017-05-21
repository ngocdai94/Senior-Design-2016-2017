import serial, time, datetime, sys
from xbee import XBee, DigiMesh, ZigBee
import sqlite3
import string

#Globals
SERIALPORT = "/dev/ttyUSB0"    # the com/serial port the XBee is connected to, the pi GPIO should always be ttyAMA0
BAUDRATE = 9600            # the baud rate we talk to the xbee
door = '\x00\x13\xa2\x00@\xe56\x8f'
analog = '\x00\x13\xa2\x00@\xe8\x98\xae'
date = time.strftime("%y/%m/%d")

#open hubDatabase.sql
conn = sqlite3.connect('/home/pi/DataHub/hubDatabase.sql')

#get cursor
curs = conn.cursor()

TEMP = 'Temperature'
HUMID = 'Humidity'
DOORSTAT = 'Door Status'

#Mac Addresses
macTempHumid = '0013a20040e53693'
macDoor = '0013a20040e5368f'

#End Globals
def insertTemp(data,date,time):
    curs.execute('''
    INSERT INTO sensorList(date, time, sensorID, sensorType, data)
    VALUES(?,?,?,?,?)''', (date, time, macTempHumid, TEMP, data))
    conn.commit()

def insertHumid(data,date,time):
    curs.execute('''
    INSERT INTO sensorList(date, time, sensorID, sensorType, data)
    VALUES(?,?,?,?,?)''', (date, time, macTempHumid, HUMID, data))
    conn.commit()

def insertDoor(data,date,time):
    curs.execute('''
    INSERT INTO sensorList(date, time, sensorID, sensorType, data)
    VALUES(?,?,?,?,?)''', (date, time, macDoor, DOORSTAT, data))
    conn.commit()


def getCurrentTime():
    return time.strftime("%H:%M")

def getdoor(data):
    #iterate over data elements
    readings = []
    for item in data:
        readings.append(item.get('dio-0'))
    return readings
#end getDoor

def getXbee(data):
    #iterate over data elements
    readings = []
    for item in data:
        #status = "".join('{}_{}'.format(k,v) for k,v in item)
        readings.append(item.get('adc-0'))
    return readings
#end getXbee

def main():
    global date
    SERIALPORT = "/dev/ttyUSB0"    # the com/serial port the XBee is connected to, the pi GPIO should always be ttyAMA0
    BAUDRATE = 9600            # the baud rate we talk to the xbee
    door = '\x00\x13\xa2\x00@\xe56\x8f'
    analog = '\x00\x13\xa2\x00@\xe8\x98\xae'
    ser = serial.Serial(SERIALPORT, BAUDRATE, timeout=1)

    #call Xbee
    xbee = ZigBee(ser)
    print ('Starting Up Door Monitor')
    # Continuously read and print packets
    while True:
        try:
            
            #read API packet
            response = xbee.wait_read_frame()
            ###print(response)

            #get MAC address from each Xbee
            addr = response['source_addr_long'].encode('hex')

##            #receive message
##            if response['rf_data']:
##                readings = response['rf_data'].split()
##                print(readings[0])
                
            #door sensor
            if addr == '0013a20040e5368f': # MAC Address Xbee Door
                doorStatus = getdoor(response['samples'])
                print(doorStatus) #Dai added
                #insertDoor(doorStatus,date,getCurrentTime())

            #analog sensor
            else:# addr ==  macTempHumid: #'0013a20040e898ae':
                print(getXbee(response['samples']))
                #analog = getXbee(response['samples'])
                #print (analog) #Dai added
                #insertTemp(analog,date,getCurrentTime())
                #print(addr + ': analog : ' + str(analog))
            
        except KeyboardInterrupt:
            
            break

    ser.close()
main()
#End main
