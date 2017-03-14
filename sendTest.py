#!/usr/bin/env python3

import json
from serial_port import SerialPort
from json_pkt import JSON_Packet
seqs = None

with open("sequences.json") as data_file:
	seqs = json.load(data_file)

port = SerialPort("/dev/ttyACM0")

jpkt = JSON_Packet(port,show_packets=True)

jpkt.send(seqs)
while True:
	byte = port.read_byte()
	if byte is not None:
		obj = jpkt.process_byte(byte)
		if obj is not None:
			print('Rcvd', obj)
			break
