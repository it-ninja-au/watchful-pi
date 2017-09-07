#!/usr/bin/env python
import os
import sys
import time
import datetime
import redis
import RPi.GPIO as GPIO
import uploadRedis

DIO = 13
CLK = 12
STB = 11

LSBFIRST = 0
MSBFIRST = 1

tmp = 0
sleep_duration = 20
#----------------------------------------------------------------
#	Note:
#		ds18b20's data pin must be connected to pin7(GPIO4).
#----------------------------------------------------------------

#Display Code

def _shiftOut(dataPin, clockPin, bitOrder, val):
	for i in range(8):
		if bitOrder == LSBFIRST:
			GPIO.output(dataPin, val & (1 << i))
		else:
			GPIO.output(dataPin, val & (1 << (7 -i)))
		GPIO.output(clockPin, True)
		time.sleep(0.000001)			
		GPIO.output(clockPin, False)
		time.sleep(0.000001)			
	
def sendCommand(cmd):
	GPIO.output(STB, False)
	_shiftOut(DIO, CLK, LSBFIRST, cmd)
	GPIO.output(STB, True)

def TM1638_init():
	GPIO.setwarnings(False)
	GPIO.setmode(GPIO.BOARD)
	GPIO.setup(DIO, GPIO.OUT)
	GPIO.setup(CLK, GPIO.OUT)
	GPIO.setup(STB, GPIO.OUT)
	sendCommand(0x8f)

def numberDisplay(num):
	digits = [0x3f,0x06,0x5b,0x4f,0x66,0x6d,0x7d,0x07,0x7f,0x6f]
	sendCommand(0x40)
	GPIO.output(STB, False)
	_shiftOut(DIO, CLK, LSBFIRST, 0xc0)
	_shiftOut(DIO, CLK, LSBFIRST, digits[num/1000%10])
	_shiftOut(DIO, CLK, LSBFIRST, 0x00)
	_shiftOut(DIO, CLK, LSBFIRST, digits[num/100%10])
	_shiftOut(DIO, CLK, LSBFIRST, 0x00)
	_shiftOut(DIO, CLK, LSBFIRST, digits[num/10%10])
	_shiftOut(DIO, CLK, LSBFIRST, 0x00)
	_shiftOut(DIO, CLK, LSBFIRST, digits[num%10])
	_shiftOut(DIO, CLK, LSBFIRST, 0x00)
	GPIO.output(STB, True)

def numberDisplay_dec(num):
	digits = [0x3f,0x06,0x5b,0x4f,0x66,0x6d,0x7d,0x07,0x7f,0x6f]
	integer = 0
	decimal = 0

	pro = int(num * 100)

	integer = int(pro / 100)
	decimal = int(pro % 100)

	sendCommand(0x40)
	GPIO.output(STB, False)
	_shiftOut(DIO, CLK, LSBFIRST, 0xc0)
	_shiftOut(DIO, CLK, LSBFIRST, digits[integer/10])
	_shiftOut(DIO, CLK, LSBFIRST, 0x00)
	_shiftOut(DIO, CLK, LSBFIRST, digits[integer%10] | 0x80)
	_shiftOut(DIO, CLK, LSBFIRST, 0x00)
	_shiftOut(DIO, CLK, LSBFIRST, digits[decimal/10])
	_shiftOut(DIO, CLK, LSBFIRST, 0x00)
	_shiftOut(DIO, CLK, LSBFIRST, digits[decimal%10])
	_shiftOut(DIO, CLK, LSBFIRST, 0x00)
	GPIO.output(STB, True)


# Reads temperature from all sensors found in /sys/bus/w1/devices/
# starting with "28-...
def readSensors():
	count = 0
	sensor = ""
	for file in os.listdir("/sys/bus/w1/devices/"):
		if (file.startswith("28-")):
			readSensor(file)
			count+=1
	if (count == 0):
		print "No sensor found! Check connection"

# read temperature every second for all connected sensors
def loop():
	while True:
		readSensors()
		time.sleep(sleep_duration)


# Reads temperature from sensor and prints to stdout
# id is the id of the sensor
sys.path.append('/home/pi/piper-v1')
def readSensor(id):
	tfile = open("/sys/bus/w1/devices/"+id+"/w1_slave")
	text = tfile.read()
	tfile.close()
	secondline = text.split("\n")[1]
	temperaturedata = secondline.split(" ")[9]
	temperature = float(temperaturedata[2:])
	temperature = temperature / 1000
	print "Ninja Piper in Action"
	print datetime.datetime.now()
	print "\t Current temperature is : %0.2f C" % temperature
	print "\t Uploading temperature reading to Redis..."
	uploadRedis.upload_heat_reading(temperature)
	print "\t Done uploading..."
	print "\t Updating Segment Display..."
	TM1638_init()
	#Displaying current Temperature readings on Segment display
	numberDisplay_dec(temperature)
	print "Done..can you see it?."
	print "Good, then it is sleep time for me :-)"
	print "zzzzzz"
	print "\n"
# Nothing to cleanup
def destroy():
	pass

# Main starts here
if __name__ == "__main__":
	try:
		loop()
	except KeyboardInterrupt:
		destroy()