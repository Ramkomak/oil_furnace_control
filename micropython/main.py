import machine
import time

led_pin = machine.Pin("LED", machine.Pin.OUT)

while True:
    led_pin.toggle()
    time.sleep(1)