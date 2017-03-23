#!/usr/bin/env python

import time
import argparse
import os
import glob
import signal

import json
import serial_port
from serial_port import SerialPort
from pkt import Packet

keep_reading = True


def signal_handler_end_program(signal, frame):
	global keep_reading
	keep_reading = False

def find_dir(vendor):
	if vendor == 'bruker':
		general_directory = glob.glob('/opt/PV*/data/mri/')
		if len(general_directory)>1:
			raise RuntimeError('Multiple versions of ParaVision found. List of folders found: ' + str(general_directory))
		elif len(general_directory) == 0:
			raise RuntimeError('No directory found in /opt/PV*/data/mri/') 
		return max(glob.iglob(general_directory[0] + '*/*/fid'), key = os.path.getctimei)[:-3]   # :-3 removes the fid (which is one of the files the data from the scanner is written to)
	raise ValueError('Finding standard data path is not supported for {0} systems.'.format(vendor))

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
	parser.add_argument('--file',
			dest='file',
			action='store',
			type=str,
			help='Path to json file containing the sequences. This file is sent to the pyboard.',
			default='sequences.json')
	parser.add_argument('--storage_path',
			dest='storage_path',
			action='store',
			type=str,
			help='Path to directory where delivered sequences are stored. If not specified the sequence is stored in the folder of the most recent scan.',
			default=None)

	args = parser.parse_args()

	verbose = args.verbose

	vendor = args.vendor
	
	seq_file_name = args.file

	port_name = args.port

	storage_path = args.storage_path
	if storage_path is None:
		find_dir(vendor)			#this checks if the path can be found to notify the user of potential problems before they start the experiment
	else:
		if not os.path.isdir(storage_path):
			raise ValueError('No directory {0} exists.'.format(storage_path))
		if storage_path[-1] != '/':		#this ensures the path ends with /
			storage_path = storage_path + '/'
	file_idx = 0					#this increases for every new sequenc that is stored in storage_path and is included in the file name such that the old sequence is not overridden

	"""Establishing connection to pyboard"""
	print('Seraching port...')
	while port_name is None:
		port_name = serial_port.autoscan()
	print('MicroPython board is connected to {0}'.format(port_name))
	port = SerialPort()
	
	connected = False
	print('Connecting to {0}'.format(port_name))
	while not connected:
		connected = port.connect_serial(port_name)
		time.sleep(0.25)
	print('Connection established')
	
	
	"""Loading sequences and sending them to the board"""
	seqs = None
	
	with open(seq_file_name) as data_file:
		seqs = json.load(data_file)
	if verbose >= 2:
		pkt = Packet(port,show_packets=True)
	else:	
		pkt = Packet(port)
	
	pkt.send(seqs)
	if verbose == 1:
		print('Sequences sent to board')
	elif verbose >= 2:
		print('Sent sequences:\n' + str(seqs))
	
	"""Recieving delivered sequence and storing it in appropriate directory"""
	signal.signal(signal.SIGINT, signal_handler_end_program)
	print('Press Ctrl+c when you are done to close the program.')	
	msg = ''
	while keep_reading:
		rcvd = None
		while rcvd is None:
			byte = port.read_byte()
			if byte is not None:
				rcvd = pkt.process_byte(byte)
			elif pkt.is_safe_to_end():
				break
		if rcvd is not None:
			if type(rcvd) is str:
				print(rcvd)
				if rcvd[:6] == 'Missed':
					msg = msg + rcvd + '\n'
			else:
				if verbose > 1:
					print('Received sequence:\n' + str(rcvd))
				if storage_path is None:
					path = find_dir(vendor)
					with open(path+'sequence.json','w+') as fp:
						json.dump(rcvd,fp,sort_keys=True,indent=4,separators=(',',': '))
						print('Sequence saved as {0}'.format(path+'sequence.json'))
					if msg != '':
						with open(path+'errors.txt','w+') as fp:
							try:
								eval('print(msg,file=fp)')
							except SyntaxError:
								print >>fp, msg
							print('Error messages saved as {0}'.format(path+'errors.txt'))
				else:
					with open(storage_path+'sequece'+str(file_idx)+'.json','w+') as fp:
						json.dump(rcvd,fp,sort_keys=True,indent=4,separators=(',',': '))
						print('Sequence saved as {0}'.format(storage_path+'sequece'+str(file_idx)+'.json'))
						if msg != '':
							with open(storage_path+'errors'+str(file_idx)+'.txt','w+') as fp:
								try:
									eval('print(msg,file=fp)')
								except SyntaxError:
									print >>fp, msg
								print('Error messages saved as {0}'.format(storage_path+'errors'+str(file_idx)+'.txt'))
					file_idx += 1
	port.close_serial()

main()
