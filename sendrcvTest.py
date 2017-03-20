#!/usr/bin/env python3

import time
import argparse

import json
import serial_port
from serial_port import SerialPort
from pkt import Packet


def main():

	parser = argparse.ArgumentParser(prog="COSplay",
					description="Main program running on host computer for usage with a pyboard running COSplay")
	parser.add_argument("-v","--verbose",
			dest="verbose",
			action="store",
			type=int,
			help="Set the verbosity.",
			default='1')
	parser.add_argument('--vendor',
			dest='vendor',
			action='store',
			type=str,
			help='Is needed to find the correct folder. Program knows "bruker" (default=bruker)',
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
			help='Path to json file containing the sequences.',
			default='sequences.json')
	args = parser.parse_args()
	verbose = args.verbose
	vendor = args.vendor
	seqFileName = args.file

	"""Establishing connection to pyboard"""
	portName = args.port
	print('Seraching port...')
	while not portName:
		portName = serial_port.autoscan()
	print('MicroPython board is connected to {0}'.format(portName))
	port = SerialPort()
	
	connected = False
	print('Connecting to {0}'.format(portName))
	while not connected:
		connected = port.connect_serial(portName)
		time.sleep(0.25)
	print('Connection established')
	
	
	"""Loading sequences and sending them to the board"""
	seqs = None
	
	with open(seqFileName) as data_file:
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
	print('Press Ctrl+c when you are done to close the program.')	
	try:
		while True:
			rcvd = None
			while True:
				byte = port.read_byte()
				if byte is not None:
					rcvd = pkt.process_byte(byte)
					if rcvd is not None:
						break
			if type(rcvd) is str:
				print(rcvd)
			elif verbose >= 1:
				print('Received sequence:\n' + str(rcvd))
	except KeyboardInterrupt:
		print("Ending program!")
	
	port.close_serial()

main()
