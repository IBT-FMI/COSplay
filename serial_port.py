"""This module implements the SerialPort class, which allows the host to talk
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
        if self.serial_port:
            print('Closing serial...')
            self.serial_port.close()
        self.serial_port = None
	
    def is_byte_available(self):
        readable, _, _ = select.select([self.serial_port.fileno()], [], [], 0)
        return bool(readable)

    def read_byte(self):
        """Reads a byte from the serial port."""
        if self.is_byte_available():
            data = self.serial_port.read()
            if data:
                return data[0]

    def write(self, data):
        """Write data to a serial port."""
        self.serial_port.write(data)

def is_micropython_usb_device(port):				#function form rshell project of dhylands
    """Checks a USB device to see if it looks like a MicroPython device.
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

def autoscan():							#function form rshell project of dhylands
    """autoscan will check all of the serial ports to see if they have
       a matching VID:PID for a MicroPython board. If it matches.
    """
    for port in serial.tools.list_ports.comports():
        if is_micropython_usb_device(port):
            return port[0]
    return None


