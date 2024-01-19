from machine import Pin, Timer
import onewire
import ds18x20
from time import ticks_ms, ticks_diff


class Furnace:

    def __init__(self, flame_detector, valve, heater, fan, magneto):
        self.flame_detector_pin = Pin(flame_detector, Pin.IN, Pin.PULL_UP)
        self.valve_pin = Pin(valve, Pin.OUT, value=1)
        self.heater_pin = Pin(heater, Pin.OUT, value=1)
        self.fan_pin = Pin(fan, Pin.OUT, value=1)
        self.magneto_pin = Pin(magneto, Pin.OUT, value=1)
        self.pre_purge_time = 5000  # ms
        self.igniter_time = 6000  # ms
        self.curr_state = 1
        self.oil_temp = 25
        self.hysteresis_width = 1
        self.error_count = 0
        self.working_flag = False
        self.oil_good = False
        self.failure = False
        self.temp_sensor = ds18x20.DS18X20(onewire.OneWire(Pin(7)))
        self.temp = self.temp_sensor.scan()
        self.oil_watch = Timer()
        self.tim = Timer()
        self.start_tim = Timer()
        self.flame_watch = Timer()
        self.oil_watch.init(mode=Timer.PERIODIC, period=1000, callback=self.oil_temp_check)
        self.start_tim.init(mode=Timer.PERIODIC, period=1000, callback=self.start_procedure)
        self.up_time = 0
        self.start_time = 0

    def check_temp(self):
        self.temp_sensor.convert_temp()
        for rom in self.temp:
            return self.temp_sensor.read_temp(rom)

    def oil_temp_check(self, source):
        if self.check_temp() <= self.oil_temp - self.hysteresis_width:
            self.heater_pin.value(0)
            self.oil_good = False

        if self.check_temp() > self.oil_temp:
            self.oil_good = True

        if self.check_temp() >= self.oil_temp + self.hysteresis_width:
            self.heater_pin.value(1)
        if self.failure:
            self.heater_pin.value(1)
            self.oil_watch.deinit()

    def real_state_machine(self):

        if self.curr_state == 1:
            print("state1")
            self.fan_pin.value(0)
            self.start_tim.deinit()
            self.tim.init(mode=Timer.ONE_SHOT, period=self.pre_purge_time, callback=self.next_state)
        if self.curr_state == 2:
            print("state2")
            self.valve_pin.value(0)
            self.tim.init(mode=Timer.ONE_SHOT, period=500, callback=self.next_state)
        if self.curr_state == 3:
            print("state3")
            self.magneto_pin.value(0)
            self.tim.init(mode=Timer.ONE_SHOT, period=self.igniter_time, callback=self.next_state)
        if self.curr_state == 4:
            print("state4")
            self.magneto_pin.value(1)
            if self.flame_detector_pin.value() == 0:
                self.working_flag = True
                self.flame_watch.init(mode=Timer.PERIODIC, period=1000, callback=self.start_procedure)
                print("odpalony")
                self.start_time = ticks_ms()
            else:
                self.valve_pin.value(1)
                self.error_count += 1
                self.working_flag = False
                self.curr_state = 1
                if self.error_count < 5 and self.oil_good:
                    self.real_state_machine()
                else:
                    self.failure = True

    def next_state(self, source):
        self.curr_state += 1
        self.real_state_machine()

    def start_procedure(self, source):
        print("test")
        if self.oil_good and self.working_flag == False:
            self.real_state_machine()
        if self.working_flag and self.flame_detector_pin.value() == 1:
            self.flame_watch.deinit()
            self.valve_pin.value(1)
            self.fan_pin.value(1)
            self.working_flag = False
            self.failure = True

    def get_up_time(self):
        if self.working_flag:
            return ticks_diff(ticks_ms(), self.start_time) / 1000
        else:
            return 0




