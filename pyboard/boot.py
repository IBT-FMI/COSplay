import path
import pyb
import uos

#switch of laser immediately
pin_out = pyb.Pin('Y1',pyb.Pin.OUT_PP,pull=pyb.Pin.PULL_UP)
pin_out.value(1)

if path.exists('/flash/bootincopymode'):
	uos.remove('/flash/bootincopymode')	
	pyb.usb_mode('VCP+MSC')
	pyb.main('copymodemain.py')
else:
	pyb.usb_mode('VCP')
	pyb.main('main.py')
