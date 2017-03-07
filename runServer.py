from bluetooth import *
import threading
import sys
import time
import socket

# Globals
uuid = "fa87c0d0-afac-11de-8a39-0800200c9a66"
addr = "30:5A:3A:8E:99:4E"
connected = False
masterPort = 1

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
    server_sock=BluetoothSocket(RFCOMM)
    server_sock.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
    while connected == False:
        try:
            server_sock.bind(("",masterPort))
            server_sock.listen(masterPort)
            connected = True
        except:
            masterPort += 1
    #port = server_sock.getsockname()[1] # investigate later
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
            
            
#            clientSend.join()
            if len(data) == 0:
                break
            if not data: # if the connection is lost close the socket
                client_sock.close()
                server_sock.close()
            print(getClientData(client_sock))
            # read data from text file
            file = open("sensorData.txt","r")
            dataOut = str(file.read())
            file.close()
            # End read data from text file
            sendClientData(client_sock,dataOut)
    except IOError:
        pass

    print("disconnected")

    client_sock.close()
    server_sock.close()
    print("all done")
    
    
#end server


def main():
    
    print("Running Client/Server")
    threads = []
    # https://duckduckgo.com/?q=python+threading+example&t=raspberrypi&ia=qa&iax=1
    server()

        
#end main
main()
        
