import utime
import micropython
import random
import uos
import os.path
import os
import sys
import tsv

import config as cfg
from pulse import pulse_delivery
from stm_usb_port import USB_Port
from pkt import Packet
from error_handler import error_handler

micropython.alloc_emergency_exception_buf(100)

use_wo_server = False # use without server.
armed = False
trigger_received = False

def callback_use_wo_server():
	global use_wo_server
	use_wo_server = True

def callback_arm():
	global armed
	armed = True

def callback_trigger(line):
	global trigger_received
	trigger_received = True

def callback_trigger2():
	global trigger_received
	trigger_received = True


def main():

	#keep the following lines close to the begining of main because laser is switched on until pin_out.value(1)
	pin_out = pyb.Pin('Y1',pyb.Pin.OUT_PP,pull=pyb.Pin.PULL_UP)
	pin_out.value(1)
	pin_outLED = pyb.LED(4)
	
	global use_wo_server
	global armed
	global trigger_received

	serial_port = USB_Port()
	pkt = Packet(serial_port)

	armedLED = pyb.LED(3)			#indicates when the system is waiting for a trigger
	triggerLED = pyb.LED(2)			#indicates when the system is delivering a sequence


	try:
		file_paths = [cfg.library_path + '/' + s for s in uos.listdir(cfg.library_path)]
	except OSError:
		file_paths = []			#if path does not exist listdir raises an OSError

	sw = pyb.Switch()
	sw.callback(callback_use_wo_server)	#if button is pressed the system can be used without a server running the COSplay server application
	answer = None

	pyb.LED(2).on()
	pyb.LED(3).on()
	pyb.LED(4).on()

	#try to connect to server
	answer = pkt.ANS_no
	while not use_wo_server:
		pkt.send(pkt.INS_check_for_sequences_on_server)
		answer = pkt.receive(time_out=1)
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
		if answer == pkt.ANS_yes or len(file_paths)==0:
			pkt.send(pkt.INS_send_sequences)
			path = ''
			if os.path.exists('/sd'):
				path = '/sd/sequence_library'
			elif os.path.exists('1:'):
				path = '1:/sequence_library'			#older versions of the pyboard use 0:/ and 1:/ instead of /flash and /sd
			elif os.path.exists('/flash'):
				path = '/flash/sequence_library'
			elif os.path.exists('0:'):
				path = '0:/sequence_library'
			if not os.path.exists(path):
				uos.mkdir(path)
			for s in uos.listdir(path):
				uos.remove(path + '/' + s)
			sequence_idx = 0
			rcvd_pkt = pkt.receive()
			while type(rcvd_pkt) == list:
				with open(path+'/sequence'+str(sequence_idx)+'.tsv','w+') as fp:
					fp.write(tsv.dumps(rcvd_pkt))
				rcvd_pkt = pkt.receive()
				sequence_idx += 1
			file_paths = [path + '/' + s for s in uos.listdir(path)]
	elif len(file_paths) == 0:
			pkt.send('Error: No sequences found! You can generate sequences using COSgen.')
			raise ValueError('No sequences found on pyboard or server. Copy sequences to the sd card and specify the path in "config.py".')

	storage_path = ''		#path to folder where delivered sequences are stored if not connected to client software on server
	delivered_sequence_idx = 0	#index for naming the sequence files in storage_path
	if use_wo_server:
		if not os.path.exists('/sd/delivered_sequences'):
			uos.mkdir('/sd/delivered_sequences')
		path = '/sd/delivered_sequences/sequences'
		idx = 0
		while os.path.exists(path + str(idx)):
			idx += 1
		path = path + str(idx)
		uos.mkdir(path)
		storage_path = path
		
	eh = error_handler(use_wo_server,pkt,storage_path)

	ticks = None				#Function for utime.measurment
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
		with open(file_paths[seq_index]) as f:
			seq = tsv.load(f)
		pkt.send('Current sequence:\n'+tsv.dumps(seq))
		num_of_events = len(seq) - 1
		range_of_events = range(num_of_events-1)
		onset_column = seq[0].index('onset')
		frequency_column = seq[0].index('frequency')
		duration_column = seq[0].index('duration')
		pulse_width_column = seq[0].index('pulse_width')
		T = [int(1./seq[1][frequency_column]*conversion_factor)]
		onset = [int(seq[1][onset_column]*conversion_factor)]
		duration = [int((seq[1][onset_column]+seq[1][duration_column])*conversion_factor)]
		if T[0] < seq[1][pulse_width_column]*conversion_factor:
			pkt.send("Invalid sequence {0}. Period is smaller than pulse width. Proceeding with a different sequence.\n".format(file_paths[seq_index]))
			continue
		for i in range(2,num_of_events):
			T.append(int(1./seq[i][frequency_column]*conversion_factor))
			onset.append(int(seq[i][onset_column]*conversion_factor))
			duration.append(int((seq[i][onset_column]+seq[i][duration_column]))*conversion_factor)
			if T[i-1] < seq[i][pulse_width_column]*conversion_factor:
				pkt.send("Invalid sequence {0}. Period is smaller than pulse width. Proceeding with a different sequence.\n".format(file_paths[seq_index]))
				continue

		pkt.send('Ready to be armed!')
		sw.callback(callback_arm)
		while not armed:
			utime.sleep(0.5)
		armedLED.on()
		armed = False
		
		sw.callback(callback_trigger2)			#for test purposes the switch can be used to trigger
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
					pulse_delivery(pin_out,seq[i+1][pulse_width_column]*conversion_factor,pin_outLED,eh,ticks,sleep)
				elif utime.ticks_diff(ticks(),scheduled_time) == 0:
					pulse_delivery(pin_out,seq[i+1][pulse_width_column]*conversion_factor,pin_outLED,eh,ticks,sleep)
				elif utime.ticks_diff(ticks(),scheduled_time) > 0:
					now = ticks()
					pulse_delivery(pin_out,seq[i+1][pulse_width_column]*conversion_factor,pin_outLED,eh,ticks,sleep)
					eh.send("Missed scheduled onset time of pulse in {0} by {1} {2} ".format(i,utime.ticks_diff(now,scheduled_time),cfg.accuracy))
				scheduled_time = utime.ticks_add(scheduled_time,T[i])
		if not use_wo_server:
			pkt.send(seq)
		else:
			with open(storage_path+'/sequence'+str(delivered_sequence_idx)+'.tsv','w+') as fp:
				fp.write(tsv.dumps(seq))
			delivered_sequence_idx += 1
		armed = False
		trigger_received = False
		triggerLED.off()



try:
	main()
except Exception as e:
	#write error message to file and send them to server(does not work for syntax errors)
	serial_port = USB_Port()
	pkt = Packet(serial_port)
	with open('exceptions.txt','w+') as fp:			
		sys.print_exception(e,fp)
		pkt.send('Error on pyboard:\n' + fp.read())
	raise e
