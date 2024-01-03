from machine import Pin, I2C
from time import sleep_ms
import onewire
import ds18x20
import ssd1306

working_flag = False
oil_temp = 30
error_count = 0

pre_purge_time = 5000  # ms
igniter_time = 6000  # ms

flame_detector_pin = Pin(2, Pin.IN, Pin.PULL_UP)
valve_pin = Pin(2, Pin.OUT)
heater_pin = Pin(3, Pin.OUT)
fan_pin = Pin(4, Pin.OUT)
magneto_pin = Pin(5, Pin.OUT)
valve_pin.value(1)
heater_pin.value(1)
fan_pin.value(1)
magneto_pin.value(1)

OK_button = Pin(10, Pin.IN, Pin.PULL_UP)
UP_button = Pin(11, Pin.IN, Pin.PULL_UP)
DOWN_button = Pin(12, Pin.IN, Pin.PULL_UP)

i2c = I2C(0, sda=Pin(8), scl=Pin(9))
display = ssd1306.SSD1306_I2C(128, 64, i2c)

temp_sensor = ds18x20.DS18X20(onewire.OneWire(Pin(7)))
temp = temp_sensor.scan()


def check_temp():
    temp_sensor.convert_temp()
    sleep_ms(750)
    for rom in temp:
        return temp_sensor.read_temp(rom)


def state_machine(err):
    fan_pin.value(0)
    sleep_ms(pre_purge_time)
    valve_pin.value(0)
    sleep_ms(100)
    magneto_pin.value(0)
    sleep_ms(igniter_time)
    magneto_pin.value(1)
    if flame_detector_pin == 0:
        return True
    else:
        valve_pin.value(1)
        err += 1
        return False
def clear_display():
    display.fill(0)
    display.show()
def show_on_display(txt):
    display.fill(0)
    display.text(txt, 0, 0, 2)
    display.show()




while True:
    print("dupa")
    if check_temp() >= oil_temp:
        show_on_display('Temperature Reached!')
        state_machine(error_count)
    else:
        show_on_display('Low Temperature!')
        sleep_ms(100)
        clear_display()









