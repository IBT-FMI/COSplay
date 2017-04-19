import utime

def switch_off(pin_out, pin_outLED):
	pin_out.value(1)
	pin_outLED.off()

def switch_on(pin_out,amplitude,pin_outLED):
	pin_out.value(0)
	pin_outLED.on()

def pulse_delivery(pin_out, pulse_width, pin_outLED, pkt,ticks=utime.ticks_ms, sleep=utime.sleep_ms, amplitude=100):
	start_time = ticks()
	switch_on(pin_out,amplitude,pin_outLED)
	scheduled_time = utime.ticks_add(start_time,int(pulse_width))
	if utime.ticks_diff(ticks(),scheduled_time) < 0:
		sleep(utime.ticks_diff(scheduled_time,ticks()))
		switch_off(pin_out,pin_outLED)
	elif utime.ticks_diff(ticks(),scheduled_time) == 0:	
		switch_off(pin_out,pin_outLED)
	elif utime.ticks_diff(ticks(),scheduled_time) > 0:
		switch_off(pin_out,pin_outLED)
		pkt.send('Missed scheduled end time of pulse by {0} us'.format(utime.ticks_diff(ticks(),scheduled_time)))
