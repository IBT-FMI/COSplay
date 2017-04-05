#!/usr/bin/env python3

import time
import argparse
import os
import glob
import signal
import serial
import json
import serial_port
from pkt import Packet

keep_running = True


def signal_handler_end_program(signal, frame):
	global keep_running
	keep_running = False

def find_current_scan_dir(vendor):
	if vendor == 'bruker':
		general_directory = glob.glob('/opt/PV*/data/mri/')
		if len(general_directory)>1:
			raise RuntimeError('Multiple versions of ParaVision found. List of folders found: ' + str(general_directory))
		elif len(general_directory) == 0:
			raise RuntimeError('No directory found in /opt/PV*/data/mri/. Specif a path where the delivered sequences should be stored using the --storage_path flag.') 
		return max(glob.iglob(general_directory[0] + '*/*/fid'), key = os.path.getctime)[:-3]   # :-3 removes the fid (which is one of the files the data from the scanner is written to)
	raise ValueError('Finding standard data path is not supported for {0} systems.'.format(vendor))

def process_message(obj,error_msgs):
	if type(obj) != str:
		raise TypeError('process_message only takes string objects.')
	print(obj)
	if obj[:6] == 'Missed':
		return error_msgs + obj + '\n'
	return error_msgs

def save_sequence(obj, storage_path, file_idx, error_msgs, verbose=0):
	if type(obj) != dict:
		raise TypeError('save_sequence only stores sequences in dictionary format.')	
	if verbose > 1:
		print('Received sequence:\n' + str(rcvd))
	if storage_path is None:
		path = find_current_scan_dir(vendor)
		with open(path+'sequence.json','w+') as fp:
			json.dump(rcvd,fp,sort_keys=True,indent=4,separators=(',',': '))
			print('Sequence saved as {0}'.format(path+'sequence.json'))
		if error_msgs != '':
			with open(path+'errors.txt','w+') as fp:
				try:
					eval('print(error_msgs,file=fp)')
				except SyntaxError:
					print >>fp, error_msgs
				print('Error messages saved as {0}'.format(path+'errors.txt'))
	else:
		with open(storage_path+'sequence'+str(file_idx)+'.json','w+') as fp:
			json.dump(obj,fp,sort_keys=True,indent=4,separators=(',',': '))
			print('Sequence saved as {0}'.format(storage_path+'sequence'+str(file_idx)+'.json'))
			if error_msgs != '':
				with open(storage_path+'errors'+str(file_idx)+'.txt','w+') as fp:
					try:
						eval('print(error_msgs,file=fp)')
					except SyntaxError:
						print >>fp, error_msgs
					print('Error messages saved as {0}'.format(storage_path+'errors'+str(file_idx)+'.txt'))
	return file_idx + 1

def check_for_sequences(sequences_arg,pkt):
	if sequences_arg is not None:
		sequences_paths = glob.glob(sequences_arg)
		if len(sequences_paths) == 0:
			print('There are no sequences in {0}.'.format(sequences))
		else:
			return pkt.ANS_yes, sequences_paths
	sequences_paths = glob.glob('sequence*.json')			#this must be changed to default location of COSgen
	if len(sequences_paths) >= 1:
		print('Using most recently generated sequences from COSgen! \n')	#insert here the default path for COSgen sequences
		return pkt.ANS_yes, sequences_paths
	return pkt.ANS_no, sequences_paths

def ask_user(pkt):
	while True:
		var = input('Shall the sequences on the host be used instead of the sequences on the pyboard? (Y/n)')
		if var == 'Y':
			return pkt.ANS_yes
		elif var == 'n':
			return pkt.ANS_no
		print('"{0}" is not a valid answer. Try again!'.format(var))

def send_sequences(sequences_paths,pkt,verbose):
	if sequences_paths is not None:
		print('sending {0} sequences'.format(len(sequences_paths)))
		for path in sequences_paths:	
			with open(path) as data_file:
				seq = json.load(data_file)
				pkt.send(seq)
			if verbose == 1:
				print('Sequence {0} sent to board'.format(path))
			elif verbose >= 2:
				print('Sent sequences:\n' + str(seq))
	else:
		print('COSgen_path contains no sequences. No sequences were sent!')
	pkt.send(pkt.ANS_no) #Indicates that all sequences have been sent




def main():

	parser = argparse.ArgumentParser(prog="COSplay",
					description="Main program running on host computer for usage with a pyboard running COSplay")
	parser.add_argument('-v','--verbose',
			dest='verbose',
			action='store',
			type=int,
			help='Set the verbosity.',
			default='1')
	parser.add_argument('--vendor',
			dest='vendor',
			action='store',
			choices=['bruker'],
			type=str.lower,
			help='Is needed to find the correct folder. Program knows "bruker" (default="bruker")',
			default='bruker')
	parser.add_argument('--port',
			dest='port',
			action='store',
			type=str,
			help='Name of port pyboard is connected to. Generally not necessary as system should find the right port automatically.',
			default=None)
	parser.add_argument('--sequences',
			dest='sequences',
			action='store',
			type=str,
			help='Path to json files containing the sequences. This flag can be used if you did not save the sequences generated with COSgen in the default location or if you do not want to use the sequences generated most recently.',
			default=None)
	parser.add_argument('--storage_path',
			dest='storage_path',
			action='store',
			type=str,
			help='Path to directory where delivered sequences are stored. If not specified the sequence is stored in the folder of the most recent scan.',
			default=None)

	args = parser.parse_args()

	verbose = args.verbose

	vendor = args.vendor
	
	sequences_paths = None			#List with all paths to all sequences that will be sent to the microcontroller if requested

	port_name = args.port

	storage_path = args.storage_path
	
	if storage_path is None:
		find_current_scan_dir(vendor)			#this checks if the path can be found to notify the user of potential problems before they start the experiment
		storage_path = None
	else:
		if not os.path.isdir(storage_path):
			raise ValueError('No directory {0} exists.'.format(storage_path))
		if storage_path[-1] != '/':		#this ensures the path ends with /
			storage_path = storage_path + '/'
	file_idx = 0	#this increases for every new sequenc that is stored in storage_path and is included in the file name such that the old sequence is not overridden
	error_msgs = ''		#stores error messages that occurer while delivering one sequence

	while keep_running:
		try:
			"""Establishing connection to pyboard"""
			print('Seraching port...')
			while port_name is None:
				port_name = serial_port.autoscan()
			print('MicroPython board is connected to {0}'.format(port_name))
			port = serial_port.SerialPort()
			
			connected = False
			print('Connecting to {0}'.format(port_name))
			while not connected:
				connected = port.connect_serial(port_name)
				time.sleep(0.25)
			print('Connection established')

			if verbose >= 2:
				pkt = Packet(port,show_packets=True)
			else:	
				pkt = Packet(port)

			signal.signal(signal.SIGINT, signal_handler_end_program)
			print('Press Ctrl+c when you are done to close the program.')	
	
			while keep_running:
				obj = pkt.receive(limit_tries=2000)
				if obj == None:
					continue
				if type(obj) == str:
					error_msgs = process_message(obj,error_msgs)
				elif type(obj) == dict:
					print('Save sequece')
					file_idx =  save_sequence(obj,storage_path,file_idx,error_msgs,verbose)
				elif obj == pkt.INS_check_for_sequences_on_host:
					print('check for sequences')
					answer,sequences_paths = check_for_sequences(args.sequences,pkt)
					pkt.send(answer)
				elif obj == pkt.INS_ask_user:
					print('ask user')
					answer = ask_user(pkt)
					pkt.send(answer)
				elif obj == pkt.INS_send_sequences:
					print('send sequence')
					send_sequences(sequences_paths,pkt,verbose)
				else:
					print('Microcontroller sent unrecognised instruction! {0}'.format(str(obj)))
			port.close_serial()
		except serial.serialutil.SerialException:
			print('Serial connection interrupted')
			port_name = None
main()
