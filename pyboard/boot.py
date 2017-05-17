import pyb

sw = pyb.Switch()
start = pyb.millis()
mode = 0
active = 0
first_press_time = 0
while pyb.elapsed_millis(start) < 2000:
	if sw() == True:
		active += 1
	else:
		active = 0
	if active == 20:
		if first_press_time == 0:
			first_press_time = pyb.millis()
			mode =1
		else:
			if pyb.elapsed_time(first_press_time) < 400:
				mode = 2
	pyb.delay(1)
		
if mode == 0:
	pyb.usb_mode('VCP')
elif mode == 1:
	pyb.usb_mode('VCP')
	pyb.main('main.py')
elif mode == 2:
	pyb.usb_mode('VCP+MSC')

import micropython
micropython.alloc_emergency_exception_buf(100)
