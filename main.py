# main.py -- put your code here!

import time
import micropython
import random

import config
import fct
from stm_usb_port import USB_Port
from pkt import Packet

micropython.alloc_emergency_exception_buf(100)

armed = False
trigger_received = False
skip_receiving_file = False

class TimingErr(Exception):
	pass


def callback_trigger(line):
	global trigger_received
	trigger_received = True

def callback_trigger2():
	global trigger_received
	trigger_received = True

def callback_rcv_file():
	global skip_receiving_file
	skip_receiving_file = True

def callback_arm():
	global armed
	armed = True

def main():

	global armed
	global trigger_received
	global skip_receiving_file
	
	pin_out = pyb.Pin('Y1',pyb.Pin.OUT_PP,pull=pyb.Pin.PULL_UP)
	pin_out.value(1)
	pin_outLED = pyb.LED(4)
	
	serial_port = USB_Port()
	armedLED = pyb.LED(3)			#indicates when the system is waiting for a trigger
	triggerLED = pyb.LED(2)
	
	
	extint = pyb.ExtInt('X1', pyb.ExtInt.IRQ_FALLING, pyb.Pin.PULL_DOWN, callback_trigger)
	sw = pyb.Switch()     			
	sw.callback(callback_rcv_file)			#by pressing the switch the reception of the json file can be skiped
	seqs = None
	pkt = Packet(serial_port)
	while not skip_receiving_file:
		byte = serial_port.read_byte()
		if byte is not None:
			seqs = pkt.process_byte(byte)
			if type(seqs) is dict:
				pkt.send('Sequences received!')
				break
		time.sleep_ms(100)
	if seqs is  None:
		pkt.send('Loading {0} stored on pyboard!'.format(config.fileName))
		seqs = fct.load(config.fileName)

	seqName = "sequence0" # + random.randrange(len(seqs))

	sw.callback(callback_arm)
	pkt.send('Ready to be armed!')
	while not armed:
		time.sleep(0.5)

	while True:
		numOfEvents = len(seqs[seqName])	
		rangeOfEvents = range(0,numOfEvents)
		eventName = ["event0"]
		T = [int(1/seqs[seqName][eventName[0]]["frequency"]*1000000)]
		onset = [seqs[seqName][eventName[0]]["onset"]*1000000]
		duration = [(seqs[seqName][eventName[0]]["onset"]+seqs[seqName][eventName[0]]["duration"])*1000000]
		for i in range(1,numOfEvents):
			eventName.append("event" + str(i))
			T.append(int(1/seqs[seqName][eventName[i]]["frequency"]*1000000))
			onset.append(seqs[seqName][eventName[i]]["onset"]*1000000)
			duration.append((seqs[seqName][eventName[i]]["onset"]+seqs[seqName][eventName[i]]["duration"])*1000000)

		armedLED.on()

		sw.callback(callback_trigger2)			#for test purposes the switch can be used to trigger
		extint.enable()
		while not trigger_received:
			time.sleep_us(1)

		start_ticks = time.ticks_us()
		triggerLED.on()
		armedLED.off()
		extint.disable()
		
		for i in rangeOfEvents:
			
			scheduled_time = time.ticks_add(start_ticks,onset[i])
			end_time = time.ticks_add(start_ticks,duration[i])
			
			while time.ticks_diff(scheduled_time,end_time) < 0:
				now = time.ticks_us()
				if time.ticks_diff(now,scheduled_time) < 0:
					time.sleep_us(time.ticks_diff(scheduled_time,now))
					fct.pulse_delivery(pin_out,seqs[seqName][eventName[i]]["pulse_width"]*1000000,pin_outLED)
				elif time.ticks_diff(now,scheduled_time) == 0:
					fct.pulse_delivery(pin_out,seqs[seqName][eventName[i]]["pulse_width"]*1000000,pin_outLED)
				elif time.ticks_diff(now,scheduled_time) > 0:
					fct.pulse_delivery(pin_out,seqs[seqName][eventName[i]]["pulse_width"]*1000000,pin_outLED)
					try:				
						raise TimingErr("Missed scheduled onset time of {0}:{1} by {2} us ".format(seqName,
								eventName[i],time.ticks_diff(now,scheduled_time)))
					except TimingErr:
						pkt.send("Missed scheduled onset time of {0}:{1} by {2} us ".format(seqName,
							eventName[i],time.ticks_diff(now,scheduled_time)))
				scheduled_time = time.ticks_add(scheduled_time,T[i])

		pkt.send(seqs[seqName])

		trigger_received = False
		triggerLED.off()

		sw.callback(callback_arm)
		armed = False
		pkt.send('Ready to be armed!')
		while not armed:
			time.sleep(0.5)


main()
