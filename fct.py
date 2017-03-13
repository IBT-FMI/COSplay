import json

def load(filename):
	with open(filename) as data_file:
		data = json.load(data_file)
	return data

def switchLaserOff(laser,laserLED):
	laser.value(1)
	laserLED.off()

def switchLaserOn(laser,laserLED):
	laser.value(0)
	laserLED.on()

def laserPulse(laser,pulseWidth,laserLED):
	now = time.ticks_us()
	switchLaserOn(laser,laserLED)
	scheduled_time = time.ticks_add(now,pulseWidth*1000)
	if time.ticks_diff(now,scheduled_time) < 0:
		time.sleep_us(time.ticks_diff(scheduled_time,now))
		switchLaserOff(laser,laserLED)
	elif time.ticks_diff(now,scheduled_time) == 0:	
		switchLaserOff(laser,laserLED)
	elif time.ticks_diff(now,scheduled_time) < 0:
		raise NameError("Did not end pulse in time")
