# main.py -- put your code here!

#import json_echo

import time
import micropython
import random

import fct
from stm_usb_port import USB_Port
from json_pkt import JSON_Packet

micropython.alloc_emergency_exception_buf(100)

class TimeingErr(Exception):
	pass

def main()
	skipRecievingFile = False
	serial_port = USB_Port()
	
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
		triggerReceived = True
	
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
				break
				
	if seqs is  None:
		seqs = fct.load("sequences.json")
	
	sw.callback(callback2)			#for test purposes the switch can be used to trigger
	
	
	seqName = "sequence0" # + random.randrange(len(seqs))
	
	numOfEvents = len(seqs[seqName])	
	eventName = ["event0"]
	T = [int(1/seqs[seqName][eventName]["frequency"]*1000000)]
	for i in range(1,numOfEvents):
		eventName.append("event" + str(i))
		T.append(int(1/seqs[seqName][eventName[i]]["frequency"]*1000000))


	while not triggerReceived:
		time.sleep_us(1)

	triggerLED.on()
	print('trigger received')
	start_ticks = time.ticks_us()
	extint.disable()
	
	for i in range(0,numOfEvents):
		
		scheduled_time = time.ticks_add(start_ticks,seqs[seqName][eventName]["onset"]*1000)
		end_time = time.ticks_add(start_ticks,(seqs[seqName][eventName]["onset"]+seqs[seqName][eventName]["duration"])*1000)
		
		while time.ticks_diff(scheduled_time,end_time) < 0:
			now = time.ticks_us()
			if time.ticks_diff(now,scheduled_time) < 0:
				time.sleep_us(time.ticks_diff(scheduled_time,now))
				fct.laserPulse(laser,seqs[seqName][eventName[i]]["pulsewidth"],laserLED)
			elif time.ticks_diff(now,scheduled_time) == 0:
				fct.laserPulse(laser,seqs[seqName][eventName[i]]["pulsewidth"],laserLED)
			elif time.ticks_diff(now,scheduled_time) > 0:
				fct.laserPulse(laser,seqs[seqName][eventName[i]]["pulsewidth"],laserLED)
				raise TimingErr("Missed scheduled onset time of {0}:{1} by {2} us ".format(seqName,eventName,time.ticks_diff(now,scheduled_time)))
			scheduled_time = time.ticks_add(scheduled_time,T[i])
	
	jpkt.send(seqs[seqName])

main()