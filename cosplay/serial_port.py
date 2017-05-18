"""
Based on Dave Hylands json-ipc/serial_port.py
(https://github.com/dhylands/json-ipc.git).
This module implements the SerialPort class, which allows the host to talk
to another device using a serial like interface over a UART.
"""

import serial
import select
from serial.tools import list_ports

class SerialPort(object):
	"""Implements a PySerial port."""

	def __init__(self):
		self.serial_port = None

	def connect_serial(self, port, baud=115200):
		"""
		Try to connect to serial port.

	  	This function tries to connect to a serial port
		named 'port'.

		Parameters
		----------
		port : string
		    name of port (e.g. /dev/ttyACM0)

		Returns
		-------
		bool
		    True if connection could be established,
		    otherwise False.
		"""
		try:
			self.serial_port = serial.Serial(port=port,
                                             		 baudrate=baud,
                                             		 timeout=0.1,
                                             		 bytesize=serial.EIGHTBITS,
                                             		 parity=serial.PARITY_NONE,
                                             		 stopbits=serial.STOPBITS_ONE,
                                             		 xonxoff=False,
                                             		 rtscts=False,
                                             		 dsrdtr=False)
		except:
			return False
		return True

	def close_serial(self):
		"""Close serial connection if it is open."""
		if self.serial_port is not None:
			print('Closing serial...')
			self.serial_port.close()
		self.serial_port = None
	
	def is_byte_available(self):
		"""Check if byte can be read from serial port."""
		if self.serial_port.is_open:
			readable, _, _ = select.select([self.serial_port.fileno()], [], [], 0)
			return bool(readable)
		else:
			print('Cannot check if byte is available because port is not open.')

	def read_byte(self):
		"""Reads a byte from the serial port.

		   Returns
		   -------
		   int
		       Value of byte.
		"""
		if self.is_byte_available():
			data = self.serial_port.read()
			if type(data[0]) == int:
				return data[0]
			elif type(data[0]) == str:
				return ord(data[0])
			else:
				raise TypeError('serial_port.read() returned unrecognised type {0}'.format(type(data[0])))

	def write(self, data):
		"""Write data to a serial port.

		   Parameters
		   ----------
		   data : string / bytearray
		       Data to write.
		"""
		if self.serial_port.is_open:
			self.serial_port.write(data)
		else:
			print('Cannot write because port is not open.')

def is_micropython_usb_device(port):				#function form rshell project of dhylands
	"""Check a USB device to see if it looks like a MicroPython device.

	   Parameters
	   ----------
	   port : serial.tools.list_ports object
	       Port to check. 

	   Returns
	   -------
	   bool
	       True if device connected to 'port' looks like a MicroPython
	       device, False otherwise.
	"""
	if type(port).__name__ == 'Device':
		# Assume its a pyudev.device.Device
		if ('ID_BUS' not in port or port['ID_BUS'] != 'usb' or
		'SUBSYSTEM' not in port or port['SUBSYSTEM'] != 'tty'):
			return False
		usb_id = 'usb vid:pid={}:{}'.format(port['ID_VENDOR_ID'], port['ID_MODEL_ID'])
	else:
		# Assume its a port from serial.tools.list_ports.comports()
		usb_id = port[2].lower()
	# We don't check the last digit of the PID since there are 3 possible
	# values.
	if usb_id.startswith('usb vid:pid=f055:980'):
		return True
	# Check for Teensy VID:PID
	if usb_id.startswith('usb vid:pid=16c0:0483'):
		return True
	return False

def autoscan():						#function form rshell project of dhylands
	"""Check all serial ports to see if they are MicroPython devices.
	
	   Checks serial ports until it finds a port with matching VID:PID for
	   a MicroPython board.

	   Returns
	   -------
	   string
	       Full device name/path. None if no MicroPython device was found.
	"""
	for port in serial.tools.list_ports.comports():
		if is_micropython_usb_device(port):
			return port[0]
	return None


