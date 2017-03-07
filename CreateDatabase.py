#!/usr/bin/env python

#The purpose of this script is to generate the database
#and the tables which will be used to support processing

import sqlite3
import time

##This creates the sensor list table
def createSensorList():
    db=sqlite3.connect('/home/pi/DataHub/hubDatabase.sql')
    cursor = db.cursor()
    cursor.execute('''
        CREATE TABLE sensorList(
        date TEXT,
        time TEXT,
        sensorID INTEGER,
        sensorType TEXT,
        data FLOAT)''')
    db.commit()
    db.close()

def main():
    ##Create Database Table
    createSensorList()

##    ##These calls populate the database with defaults
##    db=sqlite3.connect('/home/pi/Desktop/hubDatabase.sql')
##    cursor = db.cursor()
##
##
##    ##populates sensor list  
##    cursor.execute('''
##        INSERT INTO sensorList(date, time, sensorID, sensorType, data)
##        VALUES(?,?,?,?,?)''', ('', '', 1, 'Temperature', 0.0))
##    db.commit()
##    
##    cursor.execute('''
##        INSERT INTO sensorList(date, time, sensorID, sensorType, data)
##        VALUES(?,?,?,?,?)''', ('', '', 2, 'Humidlity', 0.0 ))
##    db.commit()
##    
##    cursor.execute('''
##        INSERT INTO sensorList(date, time, sensorID, sensorType, data)
##        VALUES(?,?,?,?,?)''', ('', '', 3, 'Door Status', 0.0))
##    db.commit()

    #db.close()
main()

