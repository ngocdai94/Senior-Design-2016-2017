import sys
import time
import sqlite3
import socket
import serial
import string
import random

chunks = []

def parseString(inputData):
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
# end of parseString


def main():
    message = '{"foo":"ba'
    parseString(message)
    message = 'r"}~{"foo2":"bar2"}'
    parseString(message)
    parseString('~')

main()
