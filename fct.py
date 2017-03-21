import json
import time

def load(filename):
	with open(filename) as data_file:
		data = json.load(data_file)
	return data

def switch_off(pin_out, pin_outLED):
	pin_out.value(1)
	pin_outLED.off()

def switch_on(pin_out,amplitude,pin_outLED):
	pin_out.value(0)
	pin_outLED.on()

def pulse_delivery(pin_out,pulse_width,pin_outLED,amplitude=100):
	now = time.ticks_us()
	switch_on(pin_out,amplitude,pin_outLED)
	scheduled_time = time.ticks_add(now,int(pulse_width))
	if time.ticks_diff(now,scheduled_time) < 0:
		time.sleep_us(time.ticks_diff(scheduled_time,now))
		switch_off(pin_out,pin_outLED)
	elif time.ticks_diff(now,scheduled_time) == 0:	
		switch_off(pin_out,pin_outLED)
	elif time.ticks_diff(now,scheduled_time) < 0:
		raise RuntimeError("Did not end pulse in time")
