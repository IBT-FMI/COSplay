import time
import micropython
import fct

micropython.alloc_emergency_exception_buf(100)

triggerRecieved = False

triggerDuration = 1

triggerLED = pyb.LED(3)

trigger = pyb.Pin(pyb.Pin.board.X1, pyb.Pin.IN)

laser = pyb.Pin('Y1',pyb.Pin.OUT_PP,pull=pyb.Pin.PULL_UP)
laserLED = pyb.LED(2)

def switchLaser(t):
	val = laser.value()
	laser.value(not val)
	laserLED.intensity(val)					#Laser is on when laser.value() = 0 (closing the curcuit switches the laser off)

def callback1(line):
	global triggerRecieved
	triggerRecieved = True

def callback2():
	global triggerRecieved
	triggerRecieved=True


extint = pyb.ExtInt('X1', pyb.ExtInt.IRQ_FALLING, pyb.Pin.PULL_UP, callback1)

sw = pyb.Switch()
sw.callback(callback2)

seqs = fct.load("sequences.json")

micros = pyb.Timer(2, prescaler=83, period=0x3fffffff) # micro second counter cycles back to zero after approx 17min

seqName = "sequence1"
eventName = "event0"
tim = pyb.Timer(8)

while not triggerRecieved:
	time.sleep_ms(1)

#print("Trigger recieved")
triggerLED.on()
micros.counter(0)
#print("Micro counter set to zero")

for i in range(1,seqs[seqName]["numberOfEvents"]+1):
	#print("first line in loop")
	eventName = "event" + str(i)
	#print("event name set")
	tim.init(freq=seqs[seqName][eventName]["frequency"])
	#print("timer is initialised")
	while micros.counter()<seqs[seqName][eventName]["onset"]:
		time.sleep_ms(1)
	#print("event should start now")
	tim.callback(switchLaser)
	while micros.counter()<(seqs[seqName][eventName]["onset"]+seqs[seqName][eventName]["duration"]*1000000): #conversion form seconds to microseconds
		time.sleep_ms(1)
	#print("event should be done now")
	tim.callback(None)
	fct.switchLaserOff(laser,laserLED)