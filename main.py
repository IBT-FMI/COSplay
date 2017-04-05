import utime
import micropython
import random
import uos
import os.path
import os
import sys
import ujson

import config as cfg
from pulse import pulse_delivery
from stm_usb_port import USB_Port
from pkt import Packet

micropython.alloc_emergency_exception_buf(100)

use_wo_host = False # use without host.
armed = False
trigger_received = False

def callback_use_wo_host():
	global use_wo_host
	use_wo_host = True

def callback_arm():
	global armed
	armed = True

def callback_trigger(line):
	global trigger_received
	trigger_received = True

def callback_trigger2():
	global trigger_received
	trigger_received = True

def load(filename):
	with open(filename) as data_file:
		data = ujson.loads(data_file.read())
	return data

def main():

	#keep the following lines cluos. to the begining of main because laser is switched on until pin_out.value(1)
	pin_out = pyb.Pin('Y1',pyb.Pin.OUT_PP,pull=pyb.Pin.PULL_UP)
	pin_out.value(1)
	pin_outLED = pyb.LED(4)
	
	global use_wo_host
	global armed
	global trigger_received

	serial_port = USB_Port()
	pkt = Packet(serial_port)

	armedLED = pyb.LED(3)			#indicates when the system is waiting for a trigger
	triggerLED = pyb.LED(2)

	file_paths = [cfg.library_path + '/' + s for s in uos.listdir(cfg.library_path)]

	sw = pyb.Switch()
	sw.callback(callback_use_wo_host)     			
	answer = None

	pyb.LED(2).on()
	pyb.LED(3).on()
	pyb.LED(4).on()

	while not use_wo_host:
		pkt.send(pkt.INS_check_for_sequences_on_host)
		answer = pkt.receive(limit_tries=20000)
		if answer is not None:
			break

	pyb.LED(2).off()
	pyb.LED(3).off()
	pyb.LED(4).off()


	if answer == pkt.ANS_yes:
		answer = pkt.ANS_no
		if len(file_paths) >= 1:
			pkt.send(pkt.INS_ask_user)
			answer = pkt.receive()
		if answer == pkt.ANS_yes:
			pkt.send(pkt.INS_send_sequences)
		#	path = '/sd/library0/'
		#	pkt.send(path)
			path = ''
			if os.path.exists('/sd'):
				path = '/sd/library0'	
			elif os.path.exists('1:'):
				path = '1:/library0'			#older versions of the pyboard use 0:/ and 1:/ instead of /flash and /sd
			elif os.path.exists('/flash'):
				path = '/flash/library0'	
			elif os.path.exists('0:'):
				path = '0:/library0'	
			while os.path.exists(path):
				path = path[:-1] + str(int(path[-1])%10+1)
			uos.mkdir(path)
			sequence_idx = 0
			rcvd_pkt = pkt.receive()
			while type(rcvd_pkt) == dict:
				with open(path+'/sequence'+str(sequence_idx)+'.json','w+') as fp:
					fp.write(ujson.dumps(rcvd_pkt))
		#		pkt.send(str(rcvd_pkt))
				rcvd_pkt = pkt.receive()
				sequence_idx += 1
		#	file_paths = glob.glob(path+'sequence*.json')
		#	file_paths = ['/sd/library0/sequence0.json']
			file_paths = [path + '/' + s for s in uos.listdir(path)]
			for s in file_paths:
				pkt.send(s)
	elif len(file_paths) == 0:
			pkt.send('Error: No sequences found! You can generate sequences using COSgen.')

	storage_path = ''		#path to folder where delivered sequences are stored if not connected to client software on host
	delivered_sequence_idx = 0	#index for naming the sequence files in storage_path
	if use_wo_host:
		path = '/sd/delivered_sequences0'
		while os.path.exists(path):
			path = path[:-1] + str(int(path[-1])+1)
		uos.mkdir(path)
		

	ticks = None				#Holds the function for utime.measurment
	sleep = None				#Corresponding sleep function for ticks
	conversion_factor = 1			#converts seconds to the unit specified in cfg.accuracy
	if cfg.accuracy == 'us':
		ticks = utime.ticks_us
		sleep = utime.sleep_us
		conversion_factor = 1000000
	elif cfg.accuracy == 'ms':
		ticks = utime.ticks_ms
		sleep = utime.sleep_ms
		conversion_factor = 1000

	extint = pyb.ExtInt('X1', pyb.ExtInt.IRQ_FALLING, pyb.Pin.PULL_DOWN, callback_trigger)
	extint.disable()

	num_seq = len(file_paths)
	pkt.send('Size of sequence library: {0}'.format(num_seq))

	while True:
		seq_index = random.randrange(num_seq)
		seq = load(file_paths[seq_index])
		pkt.send(str(seq))
		num_of_events = len(seq)	
		range_of_events = range(0,num_of_events)
		event_name = ["event0"]
		T = [int(1/seq[event_name[0]]["frequency"]*conversion_factor)]
		onset = [seq[event_name[0]]["onset"]*conversion_factor]
		duration = [(seq[event_name[0]]["onset"]+seq[event_name[0]]["duration"])*conversion_factor]
		pkt.send('before if')
		if T[0] < seq[event_name[0]]["pulse_width"]*conversion_factor:
			pkt.send("Invalid sequence {0}. Period is smaller than pulse width. Proceeding with a different sequence.\n".format(file_paths[seq_index]))
			continue
		pkt.send('after if')
		for i in range(1,num_of_events):
			event_name.append("event" + str(i))
			T.append(int(1/seq[event_name[i]]["frequency"]*conversion_factor))
			onset.append(seq[event_name[i]]["onset"]*conversion_factor)
			duration.append((seq[event_name[i]]["onset"]+seq[event_name[i]]["duration"])*conversion_factor)
			if T[i] < seq[event_name[i]]["pulse_width"]*conversion_factor:
				pkt.send("Invalid sequence {0}. Period is smaller than pulse width. Proceeding with a different sequence.\n".format(file_paths[seq_index]))
				continue

		pkt.send('Ready to be armed!')
		sw.callback(callback_arm)
		while not armed:
			utime.sleep(0.5)
		armedLED.on()
		armed = False
		
		sw.callback(callback_trigger2)			#for test purpuos.s the switch can be used to trigger
		extint.enable()
		while not trigger_received:
			utime.sleep_us(1)

		start_ticks = ticks()
		triggerLED.on()
		armedLED.off()
		extint.disable()
		
		for i in range_of_events:
			
			scheduled_time= utime.ticks_add(start_ticks,onset[i])
			end_time= utime.ticks_add(start_ticks,duration[i])
			while utime.ticks_diff(scheduled_time,end_time) < 0:
				if utime.ticks_diff(ticks(),scheduled_time) < 0:
					sleep(utime.ticks_diff(scheduled_time,ticks()))
					pulse_delivery(pin_out,seq[event_name[i]]["pulse_width"]*conversion_factor,pin_outLED,pkt,ticks,sleep)
				elif utime.ticks_diff(ticks(),scheduled_time) == 0:
					pulse_delivery(pin_out,seq[event_name[i]]["pulse_width"]*conversion_factor,pin_outLED,pkt,ticks,sleep)
				elif utime.ticks_diff(ticks(),scheduled_time) > 0:
					now = ticks()
					pulse_delivery(pin_out,seq[event_name[i]]["pulse_width"]*conversion_factor,pin_outLED,pkt,ticks,sleep)
					pkt.send("Missed scheduled onset time of pulse in {0} by {1} {2} ".format(event_name[i],utime.ticks_diff(now,scheduled_time),cfg.accuracy))
				scheduled_time = utime.ticks_add(scheduled_time,T[i])
		if not use_wo_host:
			pkt.send(seq)
		else:
			with open(storage_path+'/sequence'+str(delivered_sequence_idx),'w+') as fp:
				fp.write(ujson.dumps(seq))
			delivered_sequence_idx += 1
		armed = False
		trigger_received = False
		triggerLED.off()





if os.path.exists('exceptions.txt'):
	uos.remove('exceptions.txt')
try:
	main()
except Exception as e:
	with open('exceptions.txt','w+') as fp:
		sys.print_exception(e,fp)
