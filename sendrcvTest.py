#!/usr/bin/env python3

import time
import argparse

import json
import serial_port
from serial_port import SerialPort
from json_pkt import JSON_Packet


VENDOR = 'Bruker'
VERBOSE = 2


def main():

	parser = argparse.ArgumentParser(prog="COSplay",
					usage="%(prog)s [options] [command]",
					description="main program running on host computer for usage with a pyboard running COSplay")
	parser.add_argument("-v","--verbose",
			dest="VERBOSE",
			action="store",
			type=int,
			help="Set the verbosity.",
			default=1)
	
	"""Establishing connection to pyboard"""
	portName = None
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
	
	
	"""Loading sequence and sending it to the board"""
	seqs = None
	
	with open("sequences.json") as data_file:
		seqs = json.load(data_file)
	if VERBOSE >= 2:
		jpkt = JSON_Packet(port,show_packets=True)
	else:	
		jpkt = JSON_Packet(port)
	
	jpkt.send(seqs)
	if VERBOSE >= 2:
		print('Sent sequence:\n' + str(seqs))
	
	"""Recieving delivered sequence and storing it in appropriate directory"""
	
	rcvdSeq = None
	while True:
		byte = port.read_byte()
		if byte is not None:
			rcvdSeq = jpkt.process_byte(byte)
			if rcvdSeq is not None:
				break
	if VERBOSE >= 2:
		print('Recieved sequence:\n' + str(rcvdSeq))

main()
