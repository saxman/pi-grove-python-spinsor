#!/usr/bin/python

import sys
import time
import math
import json
import urllib, urllib2
from multiprocessing import Process, Queue
import grovepi
import grove_rgb_lcd as lcd

## Ports for the sensors
PORT_LIGHT_SENSOR = 0 # analog
PORT_SOUND_SENSOR = 1 # analog
PORT_DHT_SENSOR = 7 # digital
PORT_ULTRASONIC_RANGER = 8 # digital
PORT_LED_BLUE = 4 # digital

## DHT sensor type for "Grove - Temperature and Humdity" sensor
DHT_SENSOR_TYPE = 0

## The sensor value that triggers the LCD to turn on
ULTRASONIC_RANGER_THRESHOLD = 20

LOG_TEXT_FORMAT = '{}\t{}\t{}\t{}\t{}\n'
LCD_TEXT_FORMAT = 'T:{}C H:{}% S:{} L:{} U:{}'

FIREBASE_URL = 'https://spinsor-b38d3.firebaseio.com/samples/saxman.json'

def store_data_proc(queue, datastore_url):
	while True:
		data = queue.get()
		post_data = json.dumps(data)
		req = urllib2.Request(datastore_url, post_data, {'Content-Type': 'application/json'})
		try:
			resp = urllib2.urlopen(req, timeout = 5)
		except Exception as e:
			sys.stderr.write(str(e) + '\n')


def log_data_proc(queue):
	with open('data', 'w') as fout:
		while True:
			data = queue.get()
			line = LOG_TEXT_FORMAT.format(data['timestamp'], data['temp'], data['hum'], data['snd'], data['light'])
			fout.write(line)
			fout.flush()


def read_data_proc(log_queue, storage_queue):
	while True:
		try:
			timestamp = long(time.time()*1000)

			## turn on blue LED to show that data is reading
			grovepi.digitalWrite(PORT_LED_BLUE, 1)

			snd = grovepi.analogRead(PORT_SOUND_SENSOR)
			if math.isnan(snd): snd = -1

			[temp, hum] = grovepi.dht(PORT_DHT_SENSOR, DHT_SENSOR_TYPE)
			if math.isnan(temp): temp = -1
			if temp < -1: temp = -1
			if math.isnan(hum): hum = -1

			light = grovepi.analogRead(PORT_LIGHT_SENSOR)
			if math.isnan(light): light = -1

			#resistance = (float)(1023 - light) * 10 / light

			usr = grovepi.ultrasonicRead(PORT_ULTRASONIC_RANGER)

			## turn off blue LED to show that data is done reading
			grovepi.digitalWrite(PORT_LED_BLUE, 0)

			## package and send the data for processing
			data = {}
			for i in ('timestamp', 'temp', 'hum', 'snd', 'light', 'usr'):
				data[i] = locals()[i]

			log_queue.put(data)
			storage_queue.put(data)

			line = LCD_TEXT_FORMAT.format(temp, hum, snd, light, usr)
			line.ljust(32)

			lcd.setText_norefresh(line)
		except Exception as e:
			sys.stderr.write(str(e) + '\n')


grovepi.pinMode(PORT_LIGHT_SENSOR, "INPUT")
grovepi.pinMode(PORT_SOUND_SENSOR, "INPUT")
grovepi.pinMode(PORT_LED_BLUE, "OUTPUT")

lcd.setRGB(0, 64, 64)
lcd_timer = 5

with open('AUTH_TOKEN', 'r') as file:
	auth_token = file.readline()

datastore_url = FIREBASE_URL + '?auth=' + auth_token

log_queue = Queue()
storage_queue = Queue()

proc = Process(target=store_data_proc, args=(storage_queue, datastore_url))
proc.daemon = True
proc.start()

proc = Process(target=log_data_proc, args=(log_queue,))
proc.daemon = True
proc.start()

proc = Process(target=read_data_proc, args=(log_queue, storage_queue))
proc.daemon = True
proc.start()

while True:
	time.sleep(1)


##
## light the lcd if the user waved their hand over the ultrasonic_rangersonic sensor
##

if ultrasonic_ranger < ULTRASONIC_RANGER_THRESHOLD:
	lcd_timer = 5

try:	
	if lcd_timer >= 0:
		lcd.setRGB(0, 64, 64)
		lcd_timer -= 1
	else:
		lcd.setRGB(0, 0, 0)
except Exception as e:
	sys.stderr.write(str(e) + '\n')
