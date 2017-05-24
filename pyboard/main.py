import utime
import micropython
import random
import uos
import path as ospath
import sys
import tsv

import config as cfg
from pulse import pulse_delivery
from stm_usb_port import USB_Port
from pkt import Packet
from error_handler import ErrorHandler

micropython.alloc_emergency_exception_buf(100)

trigger_received = False


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
	
	use_wo_server = False
	global trigger_received

	serial_port = USB_Port()
	pkt = Packet(serial_port)

	armedLED = pyb.LED(3)			#indicates when the system is waiting for a trigger
	triggerLED = pyb.LED(2)			#indicates when the system is delivering a sequence


	try:
		file_paths = [cfg.library_path + '/' + s for s in ospath.listdir_nohidden(cfg.library_path)]
	except OSError:
		file_paths = []			#if path does not exist listdir raises an OSError
	

	sw = pyb.Switch()

	pyb.LED(2).on()
	pyb.LED(3).on()
	pyb.LED(4).on()

	#try to connect to server
	answer = None
	active = 0
	debounce_time = 20
	double_click_time = 400
	send_repetition = 1000	#Generally 1sec should be enough for the computer to answer.
	reps = 0
	first_push_time = 0
	while not use_wo_server or pyb.elapsed_millis(first_push_time)<double_click_time:
		reps += 1
		if reps%send_repetition == 0:
			pkt.send(pkt.INS_check_for_sequences_on_server)
		answer = pkt.receive(time_out=1)
		if answer is not None:
			break
		if sw() == True:
			active += 1
		else:
			active = 0
			continue
		if active == debounce_time:
			if first_push_time == 0:
				first_push_time = pyb.millis()
				use_wo_server = True
			elif pyb.elapsed_millis(first_push_time) < double_click_time:
				open('/flash/bootincopymode','a').close()
				pyb.hard_reset()

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
			if ospath.exists('/sd'):
				path = '/sd/sequence_library'
			elif ospath.exists('1:'):
				path = '1:/sequence_library'			#older versions of the pyboard use 0:/ and 1:/ instead of /flash and /sd
			elif ospath.exists('/flash'):
				path = '/flash/sequence_library'
			elif ospath.exists('0:'):
				path = '0:/sequence_library'
			if not ospath.exists(path):
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
		if ospath.exists('/sd'):
			if not ospath.exists('/sd/delivered_sequences'):
				uos.mkdir('/sd/delivered_sequences')
			path = '/sd/delivered_sequences/sequences'
		elif ospath.exists('1:'):
			if not ospath.exists('1:/delivered_sequences'):
				uos.mkdir('1:/delivered_sequences')
			path = '1:/delivered_sequences/sequences'
		elif ospath.exists('/flash'):
			if not ospath.exists('/flash/delivered_sequences'):
				uos.mkdir('/flash/delivered_sequences')
			path = '/flash/delivered_sequences/sequences'
		elif ospath.exists('0:'):
			if not ospath.exists('0:/delivered_sequences'):
				uos.mkdir('0:/delivered_sequences')
			path = '0:/delivered_sequences/sequences'
			
		idx = 0
		while ospath.exists(path + str(idx)):
			idx += 1
		path = path + str(idx)
		uos.mkdir(path)
		storage_path = path
		
	eh = ErrorHandler(use_wo_server,pkt,storage_path)

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
		pulse_end = [int((seq[1][onset_column]+seq[1][duration_column])*conversion_factor)]
		num_pulses = [int(seq[1][duration_column]*conversion_factor/T[0])]
		if T[0] < seq[1][pulse_width_column]*conversion_factor:
			pkt.send("Invalid sequence {0}. Period is smaller than pulse width. Proceeding with a different sequence.\n".format(file_paths[seq_index]))
			continue
		for i in range(2,num_of_events):
			T.append(int(1./seq[i][frequency_column]*conversion_factor))
			onset.append(int(seq[i][onset_column]*conversion_factor))
			pulse_end.append(int((seq[i][onset_column]+seq[i][pulse_end_column]))*conversion_factor)
			num_pulses.append(int(seq[i][duration_column]*conversion_factor/T[i-1]))
			if T[i-1] < seq[i][pulse_width_column]*conversion_factor:
				pkt.send("Invalid sequence {0}. Period is smaller than pulse width. Proceeding with a different sequence.\n".format(file_paths[seq_index]))
				continue


		pkt.send('Ready to be armed!')
		trigger_received = False
		sw.callback(None)
		active = 0
		while active < 20:
			if sw() == True:
				active += 1
			else:
				active = 0
			pyb.delay(1)
		pyb.delay(200)
		armedLED.on()
		pkt.send('System armed!')
		
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
			pulse = 0
			while pulse < num_pulses[i]:
				if utime.ticks_diff(ticks(),scheduled_time) < 0:
					sleep(utime.ticks_diff(scheduled_time,ticks()))
					pulse_delivery(pin_out,seq[i+1][pulse_width_column]*conversion_factor,pin_outLED,eh,ticks,sleep)
				elif utime.ticks_diff(ticks(),scheduled_time) == 0:
					pulse_delivery(pin_out,seq[i+1][pulse_width_column]*conversion_factor,pin_outLED,eh,ticks,sleep)
				elif utime.ticks_diff(ticks(),scheduled_time) > 0:
					now = ticks()
					pulse_delivery(pin_out,seq[i+1][pulse_width_column]*conversion_factor,pin_outLED,eh,ticks,sleep)
					eh.send("Missed scheduled onset time of pulse in event {0} by {1} {2} ".format(i,utime.ticks_diff(now,scheduled_time),cfg.accuracy))
				scheduled_time = utime.ticks_add(scheduled_time,T[i])
				pulse += 1
		if not use_wo_server:
			pkt.send(seq)
		else:
			eh.save()
			with open(storage_path+'/sequence'+str(delivered_sequence_idx)+'.tsv','w+') as fp:
				fp.write(tsv.dumps(seq))
			delivered_sequence_idx += 1
		triggerLED.off()



try:
	main()
except Exception as e:
	#write error message to file and send them to server(does not work for syntax errors)
	serial_port = USB_Port()
	pkt = Packet(serial_port)
	with open('exceptions.txt','w+') as fp:			
		sys.print_exception(e,fp)
	with open('exceptions.txt','r') as fp:
		pkt.send('Error on pyboard:\n' + fp.read())
	raise e
