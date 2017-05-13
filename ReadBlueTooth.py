from bluetooth import * #Bluetooth yo
import time #TimeStamps
import sqlite3 #SQL Databases
import socket #Bluetooth Sockets
import string #Need Strings
import datetime

# Globals
uuid = "fa87c0d0-afac-11de-8a39-0800200c9a66"
# addr = "30:5A:3A:8E:99:4E" #nexus tablet
addr = "34:8A:7B:FE:7C:85" #Samsung Tablet
connected = False
masterPort = 1

# Parsing Globals
chunks = []
inputMessage = ''

#Database globals
dataBase = sqlite3.connect('PaccarConnect.db')
cursor = dataBase.cursor()
#end globals

#ProfileID Globals
perishables = 1
nonPerishables = 2
frozen = 3
electronics = 4
furniture = 5
misc = 6

def parseString(inputMessage):
    
    print "parseString called"
    global chunks
    endOfMessage = False
    message = ''
    #count = 0
    while (not endOfMessage):
        if (len(inputMessage) > 0):
            endOfMessage = False
        else:
           endOfMessage = True
        chunk = ''
        chunk = inputMessage
        index = chunk.find('~')
        if index == -1: # Not found
            chunks.append(chunk)
            inputMessage = ""
        else: # reached the end of a message
            if index > 0:
                chunks.append(chunk[0:index])
            message = ''.join(chunks)
            del chunks[:]
            inputMessage = chunk[index+1:] # get string from ~ to end of string
##            print "inputMessage = " + inputMessage + '\n'
##            print "message = " + message + "\n"

    return message
                
    # end of parseString

def getClientData(client_sock):

    global inputMessage
    data = client_sock.recv(2048)
    inputMessage = inputMessage + data
    return data

    #end getClientData

def closeSocketConnections(client_sock,server_sock):

    print("disconnected")
    client_sock.close()
    server_sock.close()
    print("all done")

    #end CloseSocketConnections


def server():
    global connected
    global masterPort
    global dataBase
    global cursor
    global date
    global chunks
    global inputMessage
    
    server_sock=BluetoothSocket(RFCOMM) #Initialize Server Object
    server_sock.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
    
    while connected == False: 
        try:
            server_sock.bind(("",masterPort)) #bind to given port
            server_sock.listen(masterPort)
            connected = True
        except Exception:
            masterPort += 1 # If bind fails try a new port
    
    print ("PORT NAME: ", masterPort) #Gives us info about the port
    advertise_service( server_sock, "SampleServer",
                       service_id = uuid,
                       service_classes = [ uuid, SERIAL_PORT_CLASS ],
                       profiles = [ SERIAL_PORT_PROFILE ], 
                       protocols = [ OBEX_UUID ],
                        )
    print("Waiting for connection on RFCOMM channel %d" % masterPort)

    # client_sock is where the Data will be sent via Bluetooth
    client_sock, client_info = server_sock.accept() # join the sockets
    print("Accepted connection from ", client_info)
    server_sock.setblocking(0) #non-blocking server call

    count = 0
    data = "VOID"
    dataOut = "Garbage"
    isConnected = True
    
    while isConnected:
        if len(data) == 0:
            break
        if not data: # if the connection is lost close the socket
            isConnected = False
        try:
            data = parseString(getClientData(client_sock))
            writeToQueueIn(int(data))
            count = 1
        except IOError:
            isConnected = False

    closeSocketConnections(client_sock,server_sock)

#end server

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

def writeToQueueIn(messageID):

    timeOfLog = str(datetime.datetime.now().time())[0:8]
    cursor.execute('''INSERT INTO inQueue
        (messageID, functionName, messageArrivalTime) VALUES (?,?,?)''',
        (messageID, getFunctionName(messageID), str(timeOfLog)))
    dataBase.commit()

    #End writeToQueueOut

def readOutQueue():

    cursor.execute('SELECT * FROM outQueue where rowid = 5')
    for doc in cursor:
        print(doc)

    #End readOutQueue()

def getProfileName(profileID):

    if ((porfileID < 1) or (profileID > 6)):
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


def main():
    
    print("Initializing Server Connection...")
    server()
main()
