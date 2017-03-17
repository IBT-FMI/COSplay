# main.py -- put your code here!

#import json_echo

import time
import micropython
import random

import fct

micropython.alloc_emergency_exception_buf(100)

triggerReceived = False

triggerDuration = 1

triggerLED = pyb.LED(3)

trigger = pyb.Pin(pyb.Pin.board.X1, pyb.Pin.IN)

laser = pyb.Pin('Y1',pyb.Pin.OUT_PP,pull=pyb.Pin.PULL_UP)
laserLED = pyb.LED(2)


def callback1(line):
	global triggerReceived
	triggerReceived = True

def callback2():
	global triggerReceived
	triggerReceived=True


extint = pyb.ExtInt('X1', pyb.ExtInt.IRQ_FALLING, pyb.Pin.PULL_UP, callback1)

sw = pyb.Switch()     			#for test purposes the switch can be used to trigger
sw.callback(callback2)

seqs = fct.load("sequences.json")


seqName = "sequence0"
eventName = "event0"
T = int(1/seqs[seqName][eventName]["frequency"]*1000000)

while not triggerReceived:
	time.sleep_us(1)

triggerLED.on()
print('trigger received')
start_ticks = time.ticks_us()
extint.disable()

for i in range(0,len(seqs[seqName])):
	
	eventName = "event" + str(i)
	scheduled_time = time.ticks_add(start_ticks,seqs[seqName][eventName]["onset"]*1000)
	end_time = time.ticks_add(start_ticks,(seqs[seqName][eventName]["onset"]+seqs[seqName][eventName]["duration"])*1000)
	
	while time.ticks_diff(scheduled_time,end_time) < 0:
		now = time.ticks_us()
		print('time for initialisation:')
		print(time.ticks_diff(now,start_ticks))
		if time.ticks_diff(now,scheduled_time) < 0:
			time.sleep_us(time.ticks_diff(scheduled_time,now))
			fct.laserPulse(laser,seqs[seqName][eventName]["pulsewidth"],laserLED)
		elif time.ticks_diff(now,scheduled_time) == 0:
			fct.laserPulse(laser,seqs[seqName][eventName]["pulsewidth"],laserLED)
		elif time.ticks_diff(now,scheduled_time) > 0:
			raise NameError("Missed scheduled onset time of " + seqName + ": " + eventName)
		scheduled_time = time.ticks_add(scheduled_time,T)

