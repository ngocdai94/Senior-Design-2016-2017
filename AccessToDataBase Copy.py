#accessing an SQLite database with Python
#!/usr/bin/env python

import sqlite3
import time
import string
#import format

#initial data
date = time.strftime("%y/%m/%d")
time = time.strftime("%H:%M")
#sensorType = ''
#sensorID = 0 ## sensors address
data = 0.0

#open hubDatabase.sql
conn = sqlite3.connect('/home/pi/DataHub/hubDatabase.sql')

#get cursor
curs = conn.cursor()

print "\nEntire database contents:\n"

#insert new data to current table
curs.execute('''
INSERT INTO sensorList(date, time, sensorID, sensorType, data)
VALUES(?,?,?,?,?)''', (date, time, 1, 'Temperature', 0.0))

curs.execute('''
INSERT INTO sensorList(date, time, sensorID, sensorType, data)
VALUES(?,?,?,?,?)''', (date, time, 2, '  Humidlity', 0.0))

curs.execute('''
INSERT INTO sensorList(date, time, sensorID, sensorType, data)
VALUES(?,?,?,?,?)''', (date, time, 3, 'Door Status', 0.0))
conn.commit()

#excute profileList, then print everything in the list
for row in curs.execute("SELECT * FROM sensorList"):
    print row

#If we want to access columns by name we need to set
#row_factory to sqlite3.Row class
conn.row_factory = sqlite3.Row;

print "\nDate     	Time		SensorID	    Sensor Type         Data"
print "=============================================================================="

#execute profile list and print data from profile
curs.execute("SELECT * FROM sensorList")
for reading in curs.fetchall():
    print (str(reading[0]) + "        " +
           str(reading[1]) + "               " +
           str(reading[2]) + "               " +
           '{:^10}'.format(str(reading[3])) + "           " +
           '{:10.5}'.format(str(reading[4])))

conn.close();
