#!/usr/bin/python

from flask import Flask
import time
from datetime import datetime
import cgi
import os
import RPi.GPIO as GPIO
import usonic
from io import open


app = Flask(__name__)

@app.route("/")
def hello():
    #Grab well tank level
    tankPercentFull = usonic.reading(0)

    #Access and read temperature
    id = '28-021502fbc0ff'
    mytemp = ''
    filename = 'w1_slave'
    f = open('/sys/bus/w1/devices/' + id + '/' + filename, 'r')
    line = f.readline() # read 1st line
    crc = line.rsplit(' ',1)
    crc = crc[1].replace('\n', '')
    if crc=='YES':
        line = f.readline() # read 2nd line
        mytemp = line.rsplit('t=',1)
    else:
        mytemp = 9999

    f.close()


    #change temp into readable format (this is ugly, but it works)
    mytempstr = str(mytemp[-1])
    mytempstr = mytempstr.strip()
    mytempformatint = int(mytempstr) / 1000

    #Establish javascript to set the page to reload once a minute
    refresh_ms = 5000
    refresh_code = '<body onload="setInterval(function() {window.location.reload();}, 100000);">'
    
    if tankPercentFull > 100:
        wellLevel = "Full"
    else:
        wellLevel = str(tankPercentFull)[:5] + '%'
    
    return refresh_code + "<h2>Bucket Temp: " + str(mytempformatint) + " C<br>Tank Level: " + wellLevel + "</h2>\n" + last_lines("/home/pi/wellsensor/hourlyTankRecord", 25)

def graph_maker():
    pass
        

def last_lines(file, count):
    # assuming that each line of the file is 41 characters long
    #  we're going to multiply this by two to get the byte count
    #  (two because we assume that's how the characters are encoded)
    count *= 34
    # the with open syntax is a great way to interact with files
    #  because it's clean and legible and cleans up after itself
    with open(file, 'rb') as fh:
        # the file handler is hereafter called fh
        # seek tells the file handler to move it's virtual
        #  'cursor' to a position in the file.
        # the second argument of '2' tell it to start at the
        #  end of the file (ergo the seek offset is negative)
        fh.seek(-count, 2)
        # readlines() tells it to split the data into a list at
        #  all the newline characters
        lines = fh.readlines()
        # this is some python magic called a
        #  'list comprehension'.  There are many ways to use
        #  them but here it's looping over the list and
        #  running decode on all the elements and bundling them
        #  into a new list.
        lines = [line.decode() for line in lines]
        # at this point lines should be a list of strings
        #  representing each of the lines we want in the log.
        lines.reverse()
        lines = "<br>".join(lines)
        return lines 

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=80)

