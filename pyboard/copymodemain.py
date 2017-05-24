#switch laser off immediately
pin_out = pyb.Pin('Y1',pyb.Pin.OUT_PP,pull=pyb.Pin.PULL_UP)
pin_out.value(1)

pyb.LED(1).on()
