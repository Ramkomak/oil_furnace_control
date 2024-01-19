import machine
import utime as time
from machine import Pin
import micropython


class Rotary:
    ROT_UP = 1
    ROT_DOWN = 2
    SW_PRESS = 4
    SW_RELEASE = 8

    def __init__(self, up, down, sw):
        self.up_pin = Pin(up, Pin.IN, Pin.PULL_UP)
        self.down_pin = Pin(down, Pin.IN, Pin.PULL_UP)
        self.sw_pin = Pin(sw, Pin.IN, Pin.PULL_UP)
        self.last_status = (self.up_pin.value() << 1) | self.down_pin.value()
        self.up_pin.irq(handler=self.rotary_change, trigger=Pin.IRQ_FALLING | Pin.IRQ_RISING)
        self.down_pin.irq(handler=self.rotary_change, trigger=Pin.IRQ_FALLING | Pin.IRQ_RISING)
        self.sw_pin.irq(handler=self.switch_detect, trigger=Pin.IRQ_FALLING | Pin.IRQ_RISING)
        self.handlers = []
        self.last_button_status = self.sw_pin.value()

    def rotary_change(self, pin):
        new_status = (self.up_pin.value() << 1) | self.down_pin.value()
        if new_status == self.last_status:
            return
        transition = (self.last_status << 2) | new_status
        if transition == 0b1110:
            micropython.schedule(self.call_handlers, Rotary.ROT_UP)
        elif transition == 0b1101:
            micropython.schedule(self.call_handlers, Rotary.ROT_DOWN)
        self.last_status = new_status

    def switch_detect(self, pin):
        if self.last_button_status == self.sw_pin.value():
            return
        self.last_button_status = self.sw_pin.value()
        if self.sw_pin.value():
            micropython.schedule(self.call_handlers, Rotary.SW_RELEASE)
        else:
            micropython.schedule(self.call_handlers, Rotary.SW_PRESS)

    def add_handler(self, handler):
        self.handlers.append(handler)

    def call_handlers(self, type):
        for handler in self.handlers:
            handler(type)