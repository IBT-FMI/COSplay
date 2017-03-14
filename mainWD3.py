# main.py -- put your code here!

#import json_echo

import time
import micropython
import random

import fct
from stm_usb_port import USB_Port
from json_pkt import JSON_Packet

micropython.alloc_emergency_exception_buf(100)

skipRecievingFile = False
serial_port = USB_Port()

triggerRecieved = False

triggerDuration = 1

triggerLED = pyb.LED(3)

trigger = pyb.Pin(pyb.Pin.board.X1, pyb.Pin.IN)

laser = pyb.Pin('Y1',pyb.Pin.OUT_PP,pull=pyb.Pin.PULL_UP)
laserLED = pyb.LED(2)


def callback1(line):
	global triggerRecieved
	triggerRecieved = True

def callback2():
	global triggerRecieved
	triggerRecieved = True

def callback3():
	global skipRecievingFile
	skipRecievingFile = True

extint = pyb.ExtInt('X1', pyb.ExtInt.IRQ_FALLING, pyb.Pin.PULL_UP, callback1)

sw = pyb.Switch()     			
sw.callback(callback3)			#by pressing the switch the reception of the json file can be skiped

seqs = None
jpkt = JSON_Packet(serial_port)

while not skipRecievingFile:
	byte = serial_port.read_byte()
	if byte is not None:
		seqs = jpkt.process_byte(byte)
		if seqs is not None:
			jpkt.send(seqs)
			
if seqs is  None:
	seqs = fct.load("sequences.json")

sw.callback(callback2)			#for test purposes the switch can be used to trigger


seqName = "sequence0" # + random.randrange(len(seqs))
eventName = "event0"
T = int(1/seqs[seqName][eventName]["frequency"]*1000000)

while not triggerRecieved:
	time.sleep_us(1)

triggerLED.on()
print('trigger recieved')
start_ticks = time.ticks_us()
extint.disable()

for i in range(0,len(seqs[seqName])):
	
	eventName = "event" + str(i)
	scheduled_time = time.ticks_add(start_ticks,seqs[seqName][eventName]["onset"]*1000)
	end_time = time.ticks_add(start_ticks,(seqs[seqName][eventName]["onset"]+seqs[seqName][eventName]["duration"])*1000)
	
	while time.ticks_diff(scheduled_time,end_time) < 0:
		now = time.ticks_us()
		#print('time for initialisation:')
		#print(time.ticks_diff(now,start_ticks))
		if time.ticks_diff(now,scheduled_time) < 0:
			time.sleep_us(time.ticks_diff(scheduled_time,now))
			fct.laserPulse(laser,seqs[seqName][eventName]["pulsewidth"],laserLED)
		elif time.ticks_diff(now,scheduled_time) == 0:
			fct.laserPulse(laser,seqs[seqName][eventName]["pulsewidth"],laserLED)
		elif time.ticks_diff(now,scheduled_time) > 0:
			raise NameError("Missed scheduled onset time of " + seqName + ": " + eventName)
		scheduled_time = time.ticks_add(scheduled_time,T)

