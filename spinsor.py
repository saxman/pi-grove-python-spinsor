#!/usr/bin/python

import sys
import time
import grovepi
import grove_rgb_lcd as lcd

light_sensor = 0
grovepi.pinMode(light_sensor, "INPUT")

sound_sensor = 1
grovepi.pinMode(sound_sensor, "INPUT")

ultrasonic_ranger = 8
ultrasonic_theshold = 10

dht_sensor_port = 7
dht_sensor_type = 0

led_port = 4
grovepi.pinMode(led_port, "OUTPUT")

lcd.setRGB(0, 64, 64)
lcd_timer = 5

snd = 0
temp = 0
hum = 0
light = 0
ultra = 0

with open('data', 'w') as fout:
	while True:

		## read from the sensors
		## TODO wrap each in a try-except so that all sensors can be read despite exception
		try:
			grovepi.digitalWrite(led_port, 1)

			snd = grovepi.analogRead(sound_sensor)

			[temp, hum] = grovepi.dht(dht_sensor_port, dht_sensor_type)

			light = grovepi.analogRead(light_sensor)
			resistance = (float)(1023 - light) * 10 / light

			ultra = grovepi.ultrasonicRead(ultrasonic_ranger)

			grovepi.digitalWrite(led_port, 0)
		except IOError, e:
			sys.stderr.write(str(e))

		## write the data to disk

		t = long(time.time())
		text = '{}\t{}\t{}\t{}\t{}\t{}\n'
		s = text.format(t, temp, hum, snd, light, ultra)

		fout.write(s)
		fout.flush()

		## write the data to the display

		text = "T:{}C H:{}% S:{} L:{} U:{}"
		s = text.format(temp, hum, snd, light, ultra)

		## pad the text to ensure prior text is overwritten
		if len(s) < 32:
			for x in range(len(s), 32):
				s += " "

		lcd.setText_norefresh(s)

		## light the lcd if the user waved their hand over the ultrasonic sensor

		if ultra < ultrasonic_theshold:
			lcd_timer = 5

		if lcd_timer >= 0:
			lcd.setRGB(0, 64, 64)
			lcd_timer -= 1
		else:
			lcd.setRGB(0, 0, 0)
