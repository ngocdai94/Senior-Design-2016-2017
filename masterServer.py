from xbee import XBee, DigiMesh, ZigBee
from bluetooth import *
import threading
import sys
import time
import sqlite3
import socket
import serial
import string

# Globals
uuid = "fa87c0d0-afac-11de-8a39-0800200c9a66"
addr = "30:5A:3A:8E:99:4E"
connected = False
masterPort = 1

#readSensor Globals
#Globals
SERIALPORT = "/dev/ttyUSB0"    # the com/serial port the XBee is connected to, the pi GPIO should always be ttyAMA0
BAUDRATE = 9600            # the baud rate we talk to the xbee
door = '\x00\x13\xa2\x00@\xe56\x8f'
analog = '\x00\x13\xa2\x00@\xe8\x98\xae'
date = time.strftime("%y/%m/%d")
TEMP = 'Temperature'
HUMID = 'Humidity'
DOORSTAT = 'Door Status'

#Database globals
conn = sqlite3.connect('/home/pi/DataHub/hubDatabase.sql')
cursor = conn.cursor()
#end globals
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

def getClientData(client_sock):
    data = client_sock.recv(1024)
    return data 
    #end getClientData

def sendClientData(client_sock,dataOut):
    client_sock.send(dataOut)
    #end sendClientData

def server():
    global connected
    global masterPort
    global conn
    global cursor
    global date
    
    SERIALPORT = "/dev/ttyUSB0"    # the com/serial port the XBee is connected to, the pi GPIO should always be ttyAMA0
    BAUDRATE = 9600            # the baud rate we talk to the xbee
    door = '\x00\x13\xa2\x00@\xe56\x8f'
    analog = '\x00\x13\xa2\x00@\xe8\x98\xae'
    ser = serial.Serial(SERIALPORT, BAUDRATE, timeout=1)
    xbee = ZigBee(ser)
    
    server_sock=BluetoothSocket(RFCOMM)
    server_sock.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
    
    
    while connected == False:
        try:
            server_sock.bind(("",masterPort))
            server_sock.listen(masterPort)
            connected = True
        except Exception:
            masterPort += 1
    
    print ("PORT NAME: ", masterPort)
    advertise_service( server_sock, "SampleServer",
                       service_id = uuid,
                       service_classes = [ uuid, SERIAL_PORT_CLASS ],
                       profiles = [ SERIAL_PORT_PROFILE ], 
                       protocols = [ OBEX_UUID ],
                       # commentSchtuff
                        )
    print("Waiting for connection on RFCOMM channel %d" % masterPort)

    # client_sock is the object you will be sending data to
    client_sock, client_info = server_sock.accept()
    print("Accepted connection from ", client_info)

    count = 0

    data = "VOID"
    dataOut = "Garbage"
    try:
        while True:


##            clientReceive = threading.Thread(target=getClientData, args=("client_sock",))
##            clientReceive.start()
##            clientSend = threading.Thread(target=sendClientData, args=("client_sock","dataOut"))
##            clientSend.start()
            
            if len(data) == 0:
                break
            if not data: # if the connection is lost close the socket
                client_sock.close()
                server_sock.close()
            print(getClientData(client_sock))

            # Get data
            response = xbee.wait_read_frame()
            #print(response)
            #addr = response['source_addr_long'].endcode('hex')
            print (response[0].endcode('hex'))
            
            if response['rf_data']:
                readings = response['rf_data'].split()
            if addr == '0013a20040e5368f':
                doorStatus= getdoor(response['samples'])
                insertDoor(doorStatus,date,getCurrentTime())
            elif addr == '0013a20040e898ae':
                analog = getXbee(response['samples'])
                insertTemp(analog,date,getCurrenTime())
            #End get data

            #Dai add this line of code
            #conn = sqlite3.connect('/home/pi/DataHub/hubDatabase.sql')
            cursor.execute("SELECT * FROM sensorList")
            for reading in cursor.fetchall():
                sendClientData(client_sock,str(reading[0]) + "        " +
                       str(reading[1]) + "               " +
                       str(reading[2]) + "               " +
                       '{:^10}'.format(str(reading[3])) + "           " +
                       '{:10.5}'.format(str(reading[4])))

            #conn.close()
    except IOError:
        pass
    print("disconnected")
    client_sock.close()
    server_sock.close()
    print("all done")
#end server


def main():
    print("Running Client/Server")
    # https://duckduckgo.com/?q=python+threading+example&t=raspberrypi&ia=qa&iax=1
    server()
main()
        
