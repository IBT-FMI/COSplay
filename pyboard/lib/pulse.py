import utime

def switch_off(pin_out, pin_outLED):
	"""
	Switch off the stimulus.
	
	This function switches off the stimulus(sets pin high)
	and switches of the corresponding LED.
	
	Parameters
	----------
	pin_out : pyb.Pin object
	pin_outLED : pyb.LED object
	"""
	pin_out.value(1)
	pin_outLED.off()

def switch_on(pin_out,amplitude,pin_outLED):
	"""
	Switch on the stimulus.
	
	This function switches on the stimulus(sets pin low)
	and switches of the corresponding LED.
	
	Parameters
	----------
	pin_out : pyb.Pin object
	pin_outLED : pyb.LED object
	"""
	pin_out.value(0)
	pin_outLED.on()

def pulse_delivery(pin_out, pulse_width, pin_outLED, eh, ticks=utime.ticks_ms, sleep=utime.sleep_ms, amplitude=100):
	"""
	Deliver stimulus pulse.
	
	This function delivers a stimulus pulse of specific length.
	
	Parameters
	----------
	pin_out : pyb.Pin object
	    Channel for pulse.
	pulse_width : int
	    Duration of pulse. Unit is ticks (see ticks parameter).
	    If pulse_width ticks are exceeded before the stimulus is
	    switched off, an error message is issued.
	pin_outLED : pyb.LED object
	    Corresponding LED for stimulus type.
	eh : error_handler object form COSplay.error_handler
	ticks: time measurement function, optional
	    Default is utime.ticks_ms. Alternatively it can be set to
	    utime.ticks_us.
	sleep: sleep function, optional
	    Default is utime.sleep_ms. The sleep function
	    should match the ticks function.
	"""
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
		eh.send('Missed scheduled end time of pulse by {0} us'.format(utime.ticks_diff(ticks(),scheduled_time)))
