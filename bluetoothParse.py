import sys
import time
import sqlite3
import socket
import serial
import string
import random

chunks = []

def parseString(inputMessage):
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
        #count += 1
# end of parseString


def main():
    message = '{"foo":"bar"}~{"foo2":"bar2"}~'
    parseString(message)

main()
