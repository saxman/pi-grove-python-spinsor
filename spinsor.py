#!/usr/bin/python

import sys
import time
import math
import json
import urllib2
import socket
import ssl
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
ULTRASONIC_RANGER_THRESHOLD = 10

grovepi.pinMode(PORT_LIGHT_SENSOR, "INPUT")
grovepi.pinMode(PORT_SOUND_SENSOR, "INPUT")
grovepi.pinMode(PORT_LED_BLUE, "OUTPUT")

lcd.setRGB(0, 64, 64)
lcd_timer = 5

sound = 0
temperature = 0
humidity = 0
light = 0
ultrasonic_ranger = 0

with open('AUTH_TOKEN', 'r') as file:
	auth_token = file.readline()

request = urllib2.Request('https://spinsor-b38d3.firebaseio.com/samples/saxman.json?auth=' + auth_token)
data = {}

LOG_TEXT_FORMAT = '{}\t{}\t{}\t{}\t{}\n'
LCD_TEXT_FORMAT = 'T:{}C H:{}% S:{} L:{} U:{}'

with open('data', 'w') as fout:
	while True:

		timestamp = long(time.time())

		## TODO wrap each in a try-except so that all sensors can be read despite exception
		try:
			##
			## read from the sensors
			##

			## signal sensor data reading
			grovepi.digitalWrite(PORT_LED_BLUE, 1)

			sound = grovepi.analogRead(PORT_SOUND_SENSOR)
			if math.isnan(sound): sound = -1

			[temperature, humidity] = grovepi.dht(PORT_DHT_SENSOR, DHT_SENSOR_TYPE)
			if math.isnan(temperature): temperature = -1
			if temperature < -1: temperature = -1
			if math.isnan(humidity): humidity = -1

			light = grovepi.analogRead(PORT_LIGHT_SENSOR)
			if math.isnan(light): light = -1

			#resistance = (float)(1023 - light) * 10 / light

			ultrasonic_ranger = grovepi.ultrasonicRead(PORT_ULTRASONIC_RANGER)

			## signal sensor data reading complete
			grovepi.digitalWrite(PORT_LED_BLUE, 0)

			##
			## write the data to the display
			##

			line = LCD_TEXT_FORMAT.format(temperature, humidity, sound, light, ultrasonic_ranger)
			line.ljust(32)

			lcd.setText_norefresh(line)

		except IOError as err:
			sys.stderr.write(str(err) + '\n')
		except TypeError as err:
			sys.stderr.write(str(err) + '\n')

		##
		## write the data to disk
		##

		line = LOG_TEXT_FORMAT.format(timestamp, temperature, humidity, sound, light)

		fout.write(line)
		fout.flush()

		##
		## write the data to the cloud storage
		##

		for i in ('timestamp', 'temperature', 'humidity', 'sound', 'light'):
			data[i] = locals()[i]

		line = json.dumps(data)

		try:
			urllib2.urlopen(request, line, timeout = 1)
		except urllib2.URLError as err:
			sys.stderr.write(str(err) + '\n')
			sys.stderr.write(line + '\n')
		except socket.timeout as err:
			sys.stderr.write(str(err) + '\n')
			sys.stderr.write(line + '\n')
		except ssl.SSLError as err:
			sys.stderr.write(str(err) + '\n')
			sys.stderr.write(line + '\n')

		##
		## light the lcd if the user waved their hand over the ultrasonic_rangersonic sensor
		##

		if ultrasonic_ranger < ULTRASONIC_RANGER_THRESHOLD:
			lcd_timer = 5

		if lcd_timer >= 0:
			lcd.setRGB(0, 64, 64)
			lcd_timer -= 1
		else:
			lcd.setRGB(0, 0, 0)
