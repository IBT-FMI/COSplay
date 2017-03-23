# main.py -- put your code here!

import time
import micropython
import random
import glob
import os

import config as cfg
import fct
from stm_usb_port import USB_Port
from pkt import Packet

micropython.alloc_emergency_exception_buf(100)

armed = False
trigger_received = False
skip_receiving_file = False



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

	#keep the following lines close to the begining of main because laser is switched on until pin_out.value(1)
	pin_out = pyb.Pin('Y1',pyb.Pin.OUT_PP,pull=pyb.Pin.PULL_UP)
	pin_out.value(1)
	pin_outLED = pyb.LED(4)
	
	global armed
	global trigger_received
	global skip_receiving_file
	
	serial_port = USB_Port()
	pkt = Packet(serial_port)

	armedLED = pyb.LED(3)			#indicates when the system is waiting for a trigger
	triggerLED = pyb.LED(2)

	file_paths = glob.glob(cfg.file_name)
	if len(file_paths) >= 1:
		pkt.send(pkt.INS_check_COSgen_folder)
		answer = pkt.receive()
		if answer == True:
			pkt.send(pkt.INS_ask_user)
			answer = pkt.receive()
			if answer == pkt.ANS_use_COSgen_seqs:
				pkt.send(pkt.INS_send_sequences)
				path = ''
				if os.path.exists('/sd/')
					path = '/sd/library0/'	
				elif os.path.exists('1:/')
					path = '1:/library0/'			#older versions of the pyboard use 0:/ and 1:/ instead of /flash and /sd
				elif os.path.exists('/flash/')
					path = '/flash/library0/'	
				elif os.path.exists('0:/')
					path = '0:/library0/'	
				while os.path.exists(path):
					path = path[:-2] + str(int(path[:-1])+1)
				sequence_idx = 0
				rcvd_pkt = pkt.receive()
				while type(rcvd_pkt) == dict:
					with open(path+'sequence'+sequence_idx+'.json','w+')
					json.dump(rcvd_pkt, fp, sort_keys=True, indent=4, separators=(',',': '))
					rcvd_pkt = pkt.reveice()
				file_paths = glob.glob(path+'sequence*.json')
			
	else:
		pkt.send(pkt.INS_check_COSgen_folder)
		answer = pkt.receive()
		if answer == True:
			pkt.send(pkt.INS_send_sequences)
			path = '/SD/sequences0/'
			while os.path.exists(path):
				path = path[:-2] + str(int(path[:-1])+1)
			sequence_idx = 0
			rcvd_pkt = pkt.receive()
			while type(rcvd_pkt) == dict:
				with open(path+'sequence'+sequence_idx+'.json','w+')
				json.dump(rcvd_pkt, fp, sort_keys=True, indent=4, separators=(',',': '))
				rcvd_pkt = pkt.reveice()
			file_paths = glob.glob(path+'sequence*.json')
		else:
			pkt.send('Error: No sequences found! You can creat sequences using COSgen.')

	ticks = None				#Holds the function for time measurment
	sleep = None				#Corresponding sleep function for ticks
	conversion_factor = 1			#converts seconds to the unit specified in cfg.accuracy
	if cfg.accuracy == 'us':
		ticks = time.ticks_us
		sleep = time.sleep_us
		conversion_factor = 1000000
	elif cfg.accuracy == 'ms':
		ticks = time.ticks_ms
		sleep = time.sleep_ms
		conversion_factor = 1000



	extint = pyb.ExtInt('X1', pyb.ExtInt.IRQ_FALLING, pyb.Pin.PULL_DOWN, callback_trigger)
	sw = pyb.Switch()     			
#	sw.callback(callback_rcv_file)			#by pressing the switch the reception of the json file can be skiped
#	seqs = None
#	while not skip_receiving_file:
#		byte = serial_port.read_byte()
#		if byte is not None:
#			seqs = pkt.process_byte(byte)
#			if type(seqs) is dict:
#				pkt.send('Sequences received!')
#				break
#	if seqs is  None:
#		pkt.send('Loading {0} stored on pyboard!'.format(cfg.file_name))
#		seqs = fct.load(cfg.file_name)
	seqName = "sequence0" # + random.randrange(len(seqs))

	sw.callback(callback_arm)
	pkt.send('Ready to be armed!')
	while not armed:
		time.sleep(0.5)

	while True:
		numOfEvents = len(seqs[seqName])	
		rangeOfEvents = range(0,numOfEvents)
		eventName = ["event0"]
		T = [int(1/seqs[seqName][eventName[0]]["frequency"]*conversion_factor)]
		onset = [seqs[seqName][eventName[0]]["onset"]*conversion_factor]
		duration = [(seqs[seqName][eventName[0]]["onset"]+seqs[seqName][eventName[0]]["duration"])*conversion_factor]
		for i in range(1,numOfEvents):
			eventName.append("event" + str(i))
			T.append(int(1/seqs[seqName][eventName[i]]["frequency"]*conversion_factor))
			onset.append(seqs[seqName][eventName[i]]["onset"]*conversion_factor)
			duration.append((seqs[seqName][eventName[i]]["onset"]+seqs[seqName][eventName[i]]["duration"])*conversion_factor)

		armedLED.on()

		sw.callback(callback_trigger2)			#for test purposes the switch can be used to trigger
		extint.enable()
		while not trigger_received:
			time.sleep_us(1)

		start_ticks = ticks()
		triggerLED.on()
		armedLED.off()
		extint.disable()
		
		for i in rangeOfEvents:
			
			scheduled_time = time.ticks_add(start_ticks,onset[i])
			end_time = time.ticks_add(start_ticks,duration[i])
			while time.ticks_diff(scheduled_time,end_time) < 0:
				if time.ticks_diff(ticks(),scheduled_time) < 0:
					sleep(time.ticks_diff(scheduled_time,ticks()))
					fct.pulse_delivery(pin_out,seqs[seqName][eventName[i]]["pulse_width"]*conversion_factor,pin_outLED,pkt,ticks,sleep)
				elif time.ticks_diff(ticks(),scheduled_time) == 0:
					fct.pulse_delivery(pin_out,seqs[seqName][eventName[i]]["pulse_width"]*conversion_factor,pin_outLED,pkt,ticks,sleep)
				elif time.ticks_diff(ticks(),scheduled_time) > 0:
					fct.pulse_delivery(pin_out,seqs[seqName][eventName[i]]["pulse_width"]*conversion_factor,pin_outLED,pkt,ticks,sleep)
					pkt.send("Missed scheduled onset time of pulse in {0}:{1} by {2} {3} ".format(seqName,eventName[i],time.ticks_diff(ticks(),scheduled_time),cfg.accuracy))
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
