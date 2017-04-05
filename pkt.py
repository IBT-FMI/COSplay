# This code should run fine on MicroPython or CPython.
#
# It allows objects which can be represented as JSON objects to be sent
# between two python programs (running on the same or different computers).
try:
	from ujson import dumps
	from ujson import loads
	#from utime import ticks
except ImportError:
	from json import dumps
	from json import loads
	#from time import time

from dump_mem import dump_mem

SOH = 0x01			#start of header
STX = 0x02			#start of text
ETX = 0x03			#end of text
EOT = 0x04			#end of transmission
SEQ = 0x05			#type of data is a sequence (json)
MSG = 0x06			#type of data is message for user from pyboard
INS = 0x07			#instruction form pyboard to COSplay_host 
# <SOH><LenLow><LenHigh><TYPE><STX><PAYLOAD><ETX><LRC><EOT>

def lrc(str):
	sum = 0
	try:
		for b in str:
			sum = (sum + b) & 0xff
		return ((sum ^ 0xff) + 1) & 0xff
	except TypeError:
		for b in str:
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

	ANS_no = 0				#answers form host to instructions/questions form pyboard
	ANS_yes = 1
	INS_check_for_sequences_on_host = 2	#COSplay_host shall check for COSgen folder on host computer
	INS_ask_user = 3			#COSplay_host shall ask user whether to use sequences stored on microcontroller or host
	INS_send_sequences = 4			#COSplay_host shall send sequences to microcontroller

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
		"""Convert a python object into its json representation and then send
    	    	   it using the 'serial_port' passed in the constructor.
    	    	"""
		data_type = type(obj)
		payload_str = None
		payload_len = None
		payload_lrc = None
		if data_type is dict:
			payload_str = dumps(obj).encode('ascii')
			payload_len = len(payload_str)
			payload_lrc = lrc(payload_str)			#longitudinal redundancy check
			hdr = bytearray((SOH, payload_len & 0xff, payload_len >> 8, SEQ, STX)) #header & 0xff masks the lower eight bits(FF is 255) >>8 means shift to the right by 8 bits 
		elif data_type is str:
			payload_str = obj.encode('ascii')
			payload_len = len(payload_str)
			payload_lrc = lrc(payload_str)
			hdr = bytearray((SOH, payload_len & 0xff, payload_len >> 8, MSG, STX))
		elif data_type is int:
			payload_str = str(obj).encode('ascii')
			payload_len = len(payload_str)
			payload_lrc = lrc(payload_str)
			hdr = bytearray((SOH, payload_len & 0xff, payload_len >> 8, INS, STX))
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
		"""Process a single byte. Return a json object when one is
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
					return loads(self.pkt.decode('ascii'))
				elif self.pkt_type == MSG:
					return self.pkt.decode('ascii')
				elif self.pkt_type == INS:
					return int(self.pkt.decode('ascii'))

	def receive(self,limit_tries=0):
#		start_time = time()
#		while True:
		i = 0
		while i <= limit_tries or limit_tries == 0:
			byte = self.serial_port.read_byte()
			if byte is not None:
				limit_tries = 0
#				timeout=0	#once the functions starts to receive something it does not timeout anymore
				obj = self.process_byte(byte)
				if obj is not None:
					return obj
			i += 1
#				print(time()-start_time)
#			if time()-start_time >= timeout and timeout > 0:
#				return None

