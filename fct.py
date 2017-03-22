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

def pulse_delivery(pin_out, pulse_width, pin_outLED, pkt,ticks=time.ticks_ms, sleep=time.sleep_ms, amplitude=100):
	start_time = ticks()
	switch_on(pin_out,amplitude,pin_outLED)
	scheduled_time = time.ticks_add(start_time,int(pulse_width))
	if time.ticks_diff(ticks(),scheduled_time) < 0:
		sleep(time.ticks_diff(scheduled_time,ticks()))
		switch_off(pin_out,pin_outLED)
	elif time.ticks_diff(ticks(),scheduled_time) == 0:	
		switch_off(pin_out,pin_outLED)
	elif time.ticks_diff(ticks(),scheduled_time) > 0:
		switch_off(pin_out,pin_outLED)
		pkt.send('Missed scheduled end time of pulse by {0} us'.format(time.ticks_diff(ticks(),scheduled_time)))
