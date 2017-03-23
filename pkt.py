# This code should run fine on MicroPython or CPython.
#
# It allows objects which can be represented as JSON objects to be sent
# between two python programs (running on the same or different computers).

import json
from dump_mem import dump_mem

SOH = 0x01			#start of header
STX = 0x02			#start of text
ETX = 0x03			#end of text
EOT = 0x04			#end of transmission
SEQ = 0x05			#type of data is a sequence (json)
STA = 0x06			#type of data is status of pyboard
# <SOH><LenLow><LenHigh><TYPE><STX><PAYLOAD><ETX><LRC><EOT>

def lrc(str):
	sum = 0
	for b in str:
		try:
			sum = (sum + b) & 0xff
		except TypeError:
			sum = (sum + ord(b)) & 0xff
	return ((sum ^ 0xff) + 1) & 0xff

class Packet:

	STATE_SOH = 0
	STATE_LEN_0 = 1
	STATE_LEN_1 = 2
	STATE_TYPE = 3
	STATE_STX = 4
	STATE_PAYLOAD = 5
	STATE_ETX = 6
	STATE_LRC = 7
	STATE_EOT = 8

	def __init__(self, serial_port, show_packets=False):
		self.serial_port = serial_port
		self.show_packets = show_packets
		self.pkt_len = 0
		self.pkt_type = None
		self.pkt_idx = 0
		self.pkt = None
		self.lrc = 0
		self.state = Packet.STATE_SOH

	def send(self, obj):
		"""Converts a python object into its json representation and then sends
    	    	   it using the 'serial_port' passed in the constructor.
    	    	"""
		data_type = type(obj)
		payload_str = None
		payload_len = None
		payload_lrc = None
		if data_type is dict:
			payload_str = json.dumps(obj).encode('ascii')
			payload_len = len(payload_str)
			payload_lrc = lrc(payload_str)			#longitudinal redundancy check
			hdr = bytearray((SOH, payload_len & 0xff, payload_len >> 8, SEQ, STX)) #header & 0xff masks the lower eight bits(FF is 255) >>8 means shift to the right by 8 bits 
		elif data_type is str:
			payload_str = obj.encode('ascii')
			payload_len = len(payload_str)
			payload_lrc = lrc(payload_str)
			hdr = bytearray((SOH, payload_len & 0xff, payload_len >> 8, STA, STX)) #header & 0xff masks the lower eight bits(FF is 255) >>8 means shift to the right by 8 bits 
		else:
			raise TypeError("Type cannot be send using Packet.")
		ftr = bytearray((ETX, payload_lrc, EOT))	#footer
		if self.show_packets:
			data = hdr + payload_str + ftr
			dump_mem(data, 'Send')
		self.serial_port.write(hdr)
		self.serial_port.write(payload_str)
		self.serial_port.write(ftr)

	def process_byte(self, byte):
		"""Processes a single byte. Returns a json object when one is
    	    	   successfully parsed, otherwise returns None.
    	    	"""
		if self.show_packets:
			if byte >= ord(' ') and byte <= ord('~'):
				print('Rcvd 0x%02x \'%c\'' % (byte, byte))
			else:
				print('Rcvd 0x%02x' % byte)
		if self.state == Packet.STATE_SOH:
			if byte == SOH:
				self.state = Packet.STATE_LEN_0
		elif self.state == Packet.STATE_LEN_0:
			self.pkt_len = byte
			self.state = Packet.STATE_LEN_1
		elif self.state == Packet.STATE_LEN_1:
			self.pkt_len += (byte << 8)
			self.state = Packet.STATE_TYPE
		elif self.state == Packet.STATE_TYPE:
			self.pkt_type = byte
			self.state = Packet.STATE_STX
		elif self.state == Packet.STATE_STX:
			if byte == STX:
				self.state = Packet.STATE_PAYLOAD
				self.pkt_idx = 0
				self.pkt = bytearray(self.pkt_len)
				self.lrc = 0
			else:
				self.state = Packet.STATE_SOH
		elif self.state == Packet.STATE_PAYLOAD:
			self.pkt[self.pkt_idx] = byte
			self.lrc = (self.lrc + byte) & 0xff
			self.pkt_idx += 1
			if self.pkt_idx >= self.pkt_len:
				self.state = Packet.STATE_ETX
		elif self.state == Packet.STATE_ETX:
			if byte == ETX:
				self.state = Packet.STATE_LRC
			else:
				self.state = Packet.STATE_SOH
		elif self.state == Packet.STATE_LRC:
			self.lrc = ((self.lrc ^ 0xff) + 1) & 0xff
			if self.lrc == byte:
				self.state = Packet.STATE_EOT
			else:
				self.state = Packet.STATE_SOH
		elif self.state == Packet.STATE_EOT:
			self.state = Packet.STATE_SOH
			if byte == EOT:
				if self.pkt_type == SEQ:
					return json.loads(str(self.pkt, 'ascii'))
				elif self.pkt_type == STA:
					return str(self.pkt, 'ascii')

	def is_safe_to_end(self):
		if self.state == Packet.STATE_SOH:
			return True
		return False
