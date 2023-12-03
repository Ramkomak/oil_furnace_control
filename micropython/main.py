from machine import Pin, ADC
from math import log
from utime import sleep

thermistor_pin = ADC(10)
fan_pin = Pin(6, Pin.OUT)
valve_pin = Pin(9, Pin.OUT)
ignition_pin = Pin(7, Pin.OUT)
flame_detector_pin = Pin(4, Pin.IN)
fault_of_initial_ignition = Pin(8, Pin.OUT)
ignition_restart_button = Pin(13, Pin.OUT)

blow_through = True
restart_pressed = False

def adc_to_celsius(value_of_temp_from_adc):
    return (1/(log(1/(65535/value_of_temp_from_adc-1))/3950 + 1/298.15))


def restart_ignition(restart_button_pin):
    ignition_restart_button.irq(trigger=Pin.IRQ_FALLING, handler=restart_ignition)

#write def to ignition

while True:
    thermistor_value = thermistor_pin.read_u16()
    thermistor_value = adc_to_celsius(thermistor_value)
    if thermistor_value == 90 & blow_through == blow_through:
        fan_pin.value(1)
        sleep(5)
        fan_pin.value(0)
    else:
        valve_pin.value(1)
        ignition_pin.value(1)
        sleep(6)
        if flame_detector_pin.value() == 1:
            blow_through = False
        else:
            fault_of_initial_ignition.value(1)
            while not restart_pressed: #false by default
                sleep(0.1)

