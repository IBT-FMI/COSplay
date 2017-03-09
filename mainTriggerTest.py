
import time
import micropython

micropython.alloc_emergency_exception_buf(100)

triggerLED = pyb.LED(3)

triggerRecieved = False

def callback1(line):
	global triggerRecieved
	triggerRecieved = True	

extint = pyb.ExtInt('X1', pyb.ExtInt.IRQ_FALLING, pyb.Pin.PULL_DOWN, callback1)

while not triggerRecieved:
	time.sleep_ms(1)

triggerLED.on()
