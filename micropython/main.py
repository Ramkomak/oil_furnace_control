from machine import Pin, ADC
from math import log
from utime import sleep

temp_sensor_pin = ADC(10)
flame_detector_pin = Pin(2, Pin.IN)
heater_pin = Pin(3, Pin.OUT)
fan_pin = Pin(4, Pin.OUT)
magneto_pin = Pin(5, Pin.OUT)
valve_pin = Pin(6, Pin.OUT)
ignition_pin = Pin(7, Pin.OUT)

blow_through = True
restart_pressed = False
working_temp_reached = False

try_threshold = 4


def adc_to_celsius(value_of_temp_from_adc):
    return 1/(log(1/(65535/value_of_temp_from_adc-1))/3950 + 1/298.15)


def fan():
    fan_pin.value(1)
    sleep(5)
    fan_pin.value(0)


def magneto():
    magneto_pin.value(1)
    sleep(6)
    magneto_pin.value(0)


def temperature_check(term_val):
    if thermistor_value < 90:
        heater_pin.value(1)
    else:
        heater_pin.value(0)


while True:
    thermistor_value = temp_sensor_pin.read_u16()
    thermistor_value = adc_to_celsius(thermistor_value)

    while not working_temp_reached:
        temperature_check(thermistor_value)
    else:
        working_temp_reached = True

    if thermistor_value == 90 & blow_through == blow_through: #initialy blow_through is set to True
        fan()
        valve_pin.value(1)
        magneto()
        if flame_detector_pin.value == 0:
            for _ in range(try_threshold):
                fan()
                magneto_pin()
                if flame_detector_pin == 1:
                    valve_pin.value(0)
                    break
        elif flame_detector_pin.value == 0 & valve_pin.value() == 1:
            valve_pin.value(0)
            raise ValueError(f"Failed ignition.")
