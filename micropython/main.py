from machine import Pin, I2C, Timer
from time import sleep_ms,
import onewire
import ds18x20
import ssd1306

tim = Timer()
start_tim = Timer()
flame_watch = Timer()
oil_watch = Timer()
working_flag = False
Oil_good = False
curr_state = 1
oil_temp = 30
hysteresis_width = 1
error_count = 0

pre_purge_time = 5000  # ms
igniter_time = 6000  # ms

flame_detector_pin = Pin(2, Pin.IN, Pin.PULL_UP)
valve_pin = Pin(2, Pin.OUT, value=1)
heater_pin = Pin(3, Pin.OUT, value=1)
fan_pin = Pin(4, Pin.OUT, value=1)
magneto_pin = Pin(5, Pin.OUT, value=1)

OK_button = Pin(10, Pin.IN, Pin.PULL_UP)
UP_button = Pin(11, Pin.IN, Pin.PULL_UP)
DOWN_button = Pin(12, Pin.IN, Pin.PULL_UP)

i2c = I2C(0, sda=Pin(8), scl=Pin(9))
display = ssd1306.SSD1306_I2C(128, 64, i2c)

temp_sensor = ds18x20.DS18X20(onewire.OneWire(Pin(7)))
temp = temp_sensor.scan()


def start_procedure(Source):
    print("test")
    if Oil_good and working_flag == False:
        real_state_machine()
    if working_flag and flame_detector_pin.value() == 0:
        pass
    else:
        display.fill(0)
        display.text("AWARIA!!!",0,32,1)
        display.show()
        valve_pin.value(1)
        fan_pin.value(1)



def check_temp():
    temp_sensor.convert_temp()
    for rom in temp:
        return temp_sensor.read_temp(rom)

def next_state(Source):
    global curr_state
    curr_state += 1
    real_state_machine()

def real_state_machine():
    global curr_state, working_flag, error_count

    if curr_state == 1:
        print("state1")
        fan_pin.value(0)
        start_tim.deinit()
        tim.init(mode=Timer.ONE_SHOT, period=5000, callback=next_state)
    if curr_state == 2:
        print("state2")
        valve_pin.value(0)
        tim.init(mode=Timer.ONE_SHOT, period=500, callback=next_state)
    if curr_state == 3:
        print("state3")
        magneto_pin.value(0)
        tim.init(mode=Timer.ONE_SHOT, period=6000, callback=next_state)
    if curr_state == 4:
        print("state4")
        magneto_pin.value(1)
        if flame_detector_pin.value() == 0:
            working_flag = True
            flame_watch.init(mode=Timer.PERIODIC, period=1000, callback=start_procedure)
            print("odpalony")
        else:
            valve_pin.value(1)
            error_count += 1
            working_flag = False
            curr_state = 1
            if error_count < 5 and Oil_good:
                real_state_machine()
            else:
                pass


def clear_display():
    display.fill(0)
    display.show()


def show_on_display(txt):
    display.fill(0)
    display.text(txt, 0, 0, 1)
    display.show()


def which_button():
    if OK_button.value() == 0:
        sleep_ms(20)
        return 1
    if UP_button.value() == 0:
        sleep_ms(20)
        return 2
    if DOWN_button.value() == 0:
        sleep_ms(20)
        return 3
    else:
        return 0


def oil_temp_check(Source):
    global Oil_good
    if check_temp() <= oil_temp - hysteresis_width:
        heater_pin.value(0)
        Oil_good = False

    if check_temp() > oil_temp:
        Oil_good = True

    if check_temp() >= oil_temp + hysteresis_width:
        heater_pin.value(1)


print(flame_detector_pin.value())
start_tim.init(mode=Timer.PERIODIC, period=1000, callback=start_procedure)
oil_watch.init(mode=Timer.PERIODIC, period=1000, callback=oil_temp_check)




while True:
    # oil_temp_check()

    if heater_pin.value() == 0:
        display.text("Heater ON", 0, 32, 1)

    if which_button() == 1:
        print("button active")
        clear_display()
        display.text("Actual oil temp:", 0, 0, 1)
        display.text(str(check_temp()), 0, 16, 1)
        display.text("Temp set:", 0, 32, 1)
        display.text(str(oil_temp), 74, 32, 1)
        display.show()
        while True:
            sleep_ms(100)
            if which_button() > 1:
                break
            else:
                continue

    if Oil_good:
        show_on_display('Temperature Reached!')
        # real_state_machine()
        # working_flag = state_machine(error_count)
    else:
        show_on_display('Low Temperature!')
        sleep_ms(100)
        clear_display()










