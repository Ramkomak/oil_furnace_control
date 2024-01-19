from machine import Pin, I2C, Timer
from time import sleep_ms,
import ssd1306
from rotary import Rotary
import micropython
from furnace import Furnace
micropython.alloc_emergency_exception_buf(100)

menu_flag = False

Base = Furnace(6, 2, 3, 4, 5)

i2c = I2C(0, sda=Pin(8), scl=Pin(9))
display = ssd1306.SSD1306_I2C(128, 64, i2c)

rotary = Rotary(10,11,18)

x = 0
val = 0
def menu(change):
    global val, x, menu_flag
    if change == Rotary.ROT_UP:
        if menu_flag:
            Base.oil_temp += 1
    elif change == Rotary.ROT_DOWN:
        if menu_flag:
            Base.oil_temp -= 1
    elif change == Rotary.SW_PRESS:
        if menu_flag:
            menu_flag = False
        else:
            menu_flag = True

rotary.add_handler(menu)

while True:
    if Base.failure:
        display.fill(0)
        display.text('FAILURE!', 0, 0, 1)
        display.show()
        sleep_ms(100)
        display.fill(0)
        display.text('FAILURE!', 0, 12, 1)
        display.show()
        sleep_ms(100)
        display.fill(0)
        display.text('FAILURE!', 0, 24, 1)
        display.show()
        sleep_ms(100)
    else:
        if menu_flag == False:
            display.fill(0)
            if Base.working_flag:
                display.text('Working', 0, 0, 1)
            if Base.oil_good == False:
                display.text('Low Temperature!', 0, 12, 1)
                display.text('Heater ON', 0, 24, 1)
            if Base.oil_good:
                display.text('Oil Good!', 0, 12, 1)
                display.text('Heater OFF', 0, 24, 1)
            display.show()
        if menu_flag:
            display.fill(0)
            display.text('Set oil temp:', 0, 0, 1)
            display.text(str(Base.oil_temp),106,0,1)
            display.text('Other parameters',0,12,1)
            display.text('up time:',0,24,1)
            display.text(str(round(Base.get_up_time(),2)),64,24,1)
            display.text('current oil temp:',0,36,1)
            display.text(str(Base.check_temp()),64,48,1)
            display.show()






