import path
import pyb
import uos

if path.exists('/flash/bootincopymode'):
	uos.remove('/flash/bootincopymode')	
	pyb.usb_mode('VCP+MSC')
	pyb.main('copymodemain.py')
else:
	pyb.usb_mode('VCP')
	pyb.main('main.py')
