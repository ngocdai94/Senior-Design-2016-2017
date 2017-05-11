from bluetooth import * #Bluetooth yo
import time #TimeStamps
import sqlite3 #SQL Databases
import socket #Bluetooth Sockets
import string #Need Strings

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
conn = sqlite3.connect('/home/pi/DataHub/hubDatabase.sql')
cursor = conn.cursor()
#end globals

def parseString(inputMessage):
    
    print "parseString called"
    global chunks
    endOfMessage = False
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
            print "inputMessage = " + inputMessage + '\n'
            print "message = " + message + "\n"
                
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
    global conn
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
            parseString(getClientData(client_sock))
        except IOError:
            isConnected = False


    closeSocketConnections(client_sock,server_sock)

#end server

def main():
    print("Running Main")
    server()
main()
