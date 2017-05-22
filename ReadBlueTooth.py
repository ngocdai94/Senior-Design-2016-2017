from bluetooth import * #Bluetooth yo
import time #TimeStamps
import sqlite3 #SQL Databases
import socket #Bluetooth Sockets
import string #Need Strings
import datetime
import json

# Globals
#uuid = "fa87c0d0-afac-11de-8a39-0800200c9a66" # For general Android Device
uuid = "00001101-0000-1000-8000-00805f9b34fb" # For Delphi Display
# addr = "30:5A:3A:8E:99:4E" #nexus tablet
addr = "34:8A:7B:FE:7C:85" #Samsung Tablet
connected = False
masterPort = 1

#Global socket connections
GLOBAL_CLIENT_SOCK = None
GLOBAL_SERVER_SOCK = None

# Parsing Globals
chunks = []
#inputMessage = ''

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

def parseString(inputData):

    global chunks
    
    endOfInputData = False
    #count = 0
    while (not endOfInputData):
        chunk = ''
        chunk = inputData
        index = chunk.find('~')
        if index == -1: # Not found
            chunks.append(chunk)
            inputData = ""
        else: # reached the end of a message
            if index > 0:
                chunks.append(chunk[0:index])
            message = ''.join(chunks)
            del chunks[:]
            inputData = chunk[index+1:] # get string from ~ to end of string
            print "message = " + message + "\n"
            print "inputData = " + inputData + '\n'
            print "Chunks:" + ''.join(chunks)
        if (len(inputData) > 0):
            endOfInputData = False
        else:
           endOfInputData = True
        #count += 1
    return message
                
    # end of parseString

def getClientData(client_sock):

    data = client_sock.recv(2048)
    return data

    #end getClientData

def sendClientData(client_sock,dataOut):

    print(dataOut)
    client_sock.send(dataOut)

    #End sendClientData

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
   # global inputMessage
    
    server_sock=BluetoothSocket(RFCOMM) #Initialize Server Object
    server_sock.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
    GLOBAL_SERVER_SOCK = server_sock #update the global for error handling
    
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
    GLOBAL_CLIENT_SOCK = client_sock
    print("Accepted connection from ", client_info)
    server_sock.setblocking(0) #non-blocking server call
    client_sock.setblocking(0)
    
    count = 0
    data = "VOID"
    dataOut = "Garbage"
    isConnected = True
    setBTConnection(isConnected)
    junkData = '{"name":"John", "age":30,"cars":[ "Ford", "BMW", "Fiat" ]}'
    #writeToQueueIn(666, junkData)
    
    while (isConnected and verifyBTConnection()):
        if len(data) == 0:
            print ("data == 0")
            break
        if not data: # if the connection is lost close the socket
            print ("not data")
            isConnected = False
            setBTConnection(isConnected)
            client_sock.close()
            
        try:
            data = parseString(getClientData(client_sock))
            print ("ReadBluetooth.Server():Line148 data = " + data)
            messageId = getMessageId(data)
            print(data)
            writeToQueueIn(messageId,data)
        except IOError:
            #if e.args[0] == errno.EWOULDBLOCK: 
                print 'EWOULDBLOCK'
                time.sleep(1)           # short delay, no tight loops
##        else:
##            print 'e'
            

        try:
            
            if verifyOutQueueContent():
                dataOut = ''.join(str(e) for e in getOutQueueData())
                print("Output Queue Item: " + dataOut)
                #raw_input("Before Update outQueueTable")
                client_sock.send(dataOut + '~')
                #sendClientData(client_sock,dataOut)
                updateOutQueueTableProcess()
                print("Sent!")
                #raw_input("After Update outQueueTable")
        except IOError:
            print("getOutQueueData Failed or sendClietDataFailed")


    closeSocketConnections(client_sock,server_sock)

#end server

def getFunctionName(messageID): # Helper Functions

    if (messageID == 666):
        return 'INITIALIZED BLUETOOTH CONNECTION'

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


def writeToQueueIn(messageId, jsonData):
    
    jobProcessed = False
    if (messageId == 666):
        jobProcessed = True
    timeOfLog = str(datetime.datetime.now().time())[0:8]
    cursor.execute('''INSERT INTO inQueue
        (messageID, jsonData, messageArrivalTime, jobProcessed) VALUES (?,?,?,?)''',
        (messageId, jsonData, str(timeOfLog), int(jobProcessed)))
    dataBase.commit()

    #End writeToQueueOut

def readOutQueue():

    return (getOutQueueData())

    #End readOutQueue()

def getOutQueueData(): # Same as messageIDQueue in MasterDatase

    print("readOutQueue() called..")
    outQueueMessage = []
    for row in cursor.execute('''SELECT * FROM outQueue WHERE jobProcessed = 0 LIMIT 1'''):
        outQueueMessage.append(row)

    return outQueueMessage
    
    #End getOutQueueData
    

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

def setBTConnection(setConnection):

    print("setConnection() Called")
    if setConnection:
        cursor.execute('UPDATE btIsConnected SET isConnected = 1 LIMIT 1')
        dataBase.commit()
        return True
    else:
        cursor.execute('UPDATE btIsConnected SET isConnected = 0 LIMIT 1')
        dataBase.commit()
        return False
    
    #End setBTConnection

def verifyBTConnection():

    for isConnected in cursor.execute('SELECT * FROM btIsConnected LIMIT 1'):
        True

    return(bool(isConnected[0]))

    #End verifyBTConnection

def verifyOutQueueContent():

    
    jobToProcessExists = False
    for jobProcessed in cursor.execute('SELECT * FROM outQueue WHERE jobProcessed = 0 LIMIT 1'):
        jobToProcessExists = True
        break

    return jobToProcessExists

def updateOutQueueTableProcess():

    #cursor.execute('DELETE FROM outQueue Limit 1')
    cursor.execute('UPDATE outQueue SET jobProcessed = 1 WHERE jobProcessed = 0 Limit 1')
    dataBase.commit()
    #removeFromOutQueueTable()

def createJsonPackage():
    
    cursor.execute('''SELECT messageType FROM bluetoothOutgoing WHERE handledFlag = ?''',(False,))
    bluetoothMessageType = cursor.fetchone()
    if bluetoothMessageType[0] == messageType.sensorData:
        cursor.execute('''SELECT * FROM dataBuffer''')
        bluetoothSensorData = cursor.fetchall()
        for sensor in bluetoothSensorData:
            data = {}
            data["sensorType"] = sensor[2]
            data["value"] = sensor[3]
            data2 = {sensor[1]: data}
            data3 = {"sensorData" : data2}
            message = json.dumps(data3)
##            print(data3)
            client_sock.send(message + '~')
##            time.sleep(3)

def getMessageId(data): #Passing in a string

##  data =  '{"name":"John", "age":30,"cars":[ "Ford", "BMW", "Fiat" ]}'
    
    asciiData = bytearray(data).decode('ascii')
    jsonMessage = json.loads(asciiData)
    print("jsonMessage: " + str(jsonMessage))
    messageId = jsonMessage["messageId"]
    print("messageId: " + str(messageId))
    return messageId

    #End getMessageId()


    
    
def main():
    
    print("Initializing Server Connection...")

    verifyBTConnection()
    
    try:
        server()
    except KeyboardInterrupt:
        closeSocketConnections(GLOBAL_CLIENT_SOCK, GLOBAL_SERVER_SOCK)
        setBTConnection(False)
        print(str(datetime.datetime.now().time())[0:8])
main()
