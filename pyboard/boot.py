import path
import pyb
import uos

if path.exists('/flash/bootincopymode'):
	uos.remove('/flash/bootincopymode')	
	pyb.usb_mode('VCP+MSC')
	pyb.main('emptymain.py')
else:
	pyb.usb_mode('VCP')
	pyb.main('main.py')
