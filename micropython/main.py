from machine import Pin, I2C, Timer
from time import sleep_ms,
import ssd1306
from rotary import Rotary
import micropython
from furnace import Furnace
from umenu import *
import random
micropython.alloc_emergency_exception_buf(100)

menu_flag = False

Base = Furnace(6, 2, 3, 4, 5)

i2c = I2C(0, sda=Pin(8), scl=Pin(9))
display = ssd1306.SSD1306_I2C(128, 64, i2c)
def de_menu():
    global menu_flag
    menu_flag = False

menu = Menu(display, 4, 12)
menu.set_screen(MenuScreen('Main Menu')
    .add(SubMenuItem('Oil')
        .add(ValueItem('Change Temp', Base.oil_temp, 20, 100, 5, Base.set_oil_temp))
        .add(ValueItem('Hysteresis', Base.hysteresis_width, 0, 5, 1, Base.set_hysteresis_width))
        .add(InfoItem('Cur Temp', str(Base.check_temp()))))
    .add(SubMenuItem('Timers')
         .add(InfoItem('Prepurge [s]', str(Base.pre_purge_time/1000)))
         .add(InfoItem('Igniter [s]', str(Base.igniter_time/1000)))
         )
    .add(ConfirmItem("EXIT", de_menu, "Do you wanna do that?", ('yeah, sure!', 'nah, sorry!')))

)
##menu.draw()

up_pin = Pin(10, Pin.IN, Pin.PULL_UP)
down_pin = Pin(11, Pin.IN, Pin.PULL_UP)
menu_pin = Pin(18, Pin.IN, Pin.PULL_UP)



def menu_click(pin):
    global menu_flag
    sleep_ms(50)
    if pin.value() == 0:
        if menu_flag:
            menu.click()
        else:
            menu_flag = True
            menu.draw()

def menu_move_up(pin):
    sleep_ms(50)
    if pin.value() == 0:
        if menu_flag:
            menu.move(1)
def menu_move_down(pin):
    sleep_ms(50)
    if pin.value() == 0:
        if menu_flag:
            menu.move(-1)

menu_pin.irq(menu_click, Pin.IRQ_FALLING)
up_pin.irq(menu_move_up, Pin.IRQ_FALLING)
down_pin.irq(menu_move_down, Pin.IRQ_FALLING)


# x = 0
# val = 0
# def menu(change):
#     global val, x, menu_flag
#     if change == Rotary.ROT_UP:
#         if menu_flag:
#             Base.oil_temp += 1
#     elif change == Rotary.ROT_DOWN:
#         if menu_flag:
#             Base.oil_temp -= 1
#     elif change == Rotary.SW_PRESS:
#         if menu_flag:
#             menu_flag = False
#         else:
#             menu_flag = True
#
# rotary.add_handler(menu)

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
        if not menu_flag:
            display.fill(0)
            if Base.working_flag:
                display.text('Working', 0, 0, 1)
            if not Base.oil_good:
                display.text('Low Temperature!', 0, 12, 1)
                display.text('Heater ON', 0, 24, 1)
            if Base.oil_good:
                display.text('Oil Good!', 0, 12, 1)
                display.text('Heater OFF', 0, 24, 1)
            display.show()






