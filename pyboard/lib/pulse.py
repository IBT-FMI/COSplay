import utime

def deliver_pulse(pin_out_func, amplitude, pulse_width, pulse_sleep, pin_outLED, eh, ticks=utime.ticks_ms, sleep=utime.sleep_ms, on_state=1):
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
	pin_out_func(amplitude*on_state)
	pin_outLED.on()
	scheduled_time = utime.ticks_add(start_time,int(pulse_width))
	sleep(pulse_sleep)
	if utime.ticks_diff(ticks(),scheduled_time) < 0:
		sleep(utime.ticks_diff(scheduled_time,ticks()))
		pin_out_func(not on_state)
		pin_outLED.off()
	elif utime.ticks_diff(ticks(),scheduled_time) == 0:	
		pin_out_func(not on_state)
		pin_outLED.off()
	elif utime.ticks_diff(ticks(),scheduled_time) > 0:
		pin_out_func(not on_state)
		pin_outLED.off()
		eh.send('Missed scheduled end time of pulse by {0} us'.format(utime.ticks_diff(ticks(),scheduled_time)))
