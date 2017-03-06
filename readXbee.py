import serial, time, datetime, sys
from xbee import XBee, DigiMesh, ZigBee

def getdoor(data):
    #iterate over data elements
    readings = []
    for item in data:

        readings.append(item.get('dio-0'))

    return readings

def getXbee(data):
    #iterate over data elements
    readings = []
    for item in data:

        #status = "".join('{}_{}'.format(k,v) for k,v in item)
            
        readings.append(item.get('adc-0'))

    return readings

        
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

        #get MAC address from each Xbee
        addr = response['source_addr_long'].encode('hex')

        #door sensor
        if addr == '0013a20040e5368f':
        
            doorstatus = getdoor(response['samples'])

            print(addr + ': door open: ' + str(doorstatus))


        #analog sensor
        elif addr == '0013a20040e898ae':

            analog = getXbee(response['samples'])

            print(addr + ': analog : ' + str(analog))
        
    except KeyboardInterrupt:
        
        break

ser.close()
