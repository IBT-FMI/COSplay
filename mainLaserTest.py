#import pyb

laser = pyb.Pin('Y1',pyb.Pin.OUT_PP,pull=Pin.PULL_UP)

sw = pyb.Switch()

def switchLaser()
	val = laser.value()
	laser.value(not val)

sw.callback(lambda:pyb.LED(1).toggle())