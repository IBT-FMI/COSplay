from ws2812 import WS2812
import utime
import machine
power = machine.Pin(11,machine.Pin.OUT)
power.value(1)

# dit duration in seconds
dit = 0.5

BLACK = (0, 0, 0)
PURPLE = (30, 0, 25)
CYAN = (0, 25, 25)

IN_STRING = "-.-. .... -.-- -- . .-. .-"

led = WS2812(12,1)#WS2812(pin_num,led_count)

led.pixels_fill(CYAN)
led.pixels_show()
utime.sleep(dit*4)

while True:
    print("Henlo :3")
    for i in IN_STRING:
        if i == ".":
            led.pixels_fill(PURPLE)
            led.pixels_show()
            utime.sleep(dit)
        elif i == "-":
            led.pixels_fill(PURPLE)
            led.pixels_show()
            utime.sleep(dit*3)
        elif i ==" ":
            led.pixels_fill(BLACK)
            led.pixels_show()
            # only 2 dits; the third is carried over from the inter-signal dit.
            utime.sleep(dit*2)
        led.pixels_fill(BLACK)
        led.pixels_show()
        utime.sleep(dit)
    led.pixels_fill(BLACK)
    led.pixels_show()
    # only 6 dits; the third is carried over from the inter-signal dit.
    utime.sleep(dit*6)
