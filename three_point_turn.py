# Three point turn pseudo code
#!/usr/bin/python
# -*- coding: utf-8 -*-

from ABE_ADCPi import ADCPi
from ABE_helpers import ABEHelpers
from datetime import datetime, timedelta
import os
import logging
import sys
import drivetrain
from numpy import clip, interp


class three_point_turn:
    def __init__(self, drive):
        """ Standard Constructor """
        # set up ADC
        self.i2c_helper = ABEHelpers()
        self.bus = i2c_helper.get_smbus()
        self.adc = ADCPi(bus, 0x68, 0x69, 12)

        #define fixed values
        # red is typically 3.5V
        self.red_min = 3
        self.red = 3.5
        self.full_forward = 0.5
        self.slow_forward = 0.1
        self.full_reverse = -0.5
        self.slow_reverse = -0.1

        self.straight = 0
        self.full_left = -1
        self.rear_line_sensor = 2
        # same sensor for now
        self.front_line_sensor = 2
        self.max_rate = 2

        # Drivetrain is passed in
        self.drive = drive

    def run(self):
        """ Main call to run the three point turn script """
        # initiate camera

         #forward to turning point
        self.movesegment(T_first_segment_timeout, T_accelerating_first_segment, rear_line_sensor, full_forward, straight, slow_forward, straight)
        #first Left turn
        self.movesegment(T_left_turn_time, T_accelerating_second_segment, 0, Stopped, full_left, straight, slow_forward)
        #forward to first side line
        self.movesegment(T_third_segment_timeout, T_accelerating_third_segment, front_line_sensor, full_forward, straight, slow_forward,straight)
        #reverse portion to second side line
        self.movesegment(T_forth_segment_timeout, T_accelerating_forth_segment, rear_line_sensor, full_reverse, straight, slow_reverse, straight)
        #reverse portion to second side line
        self.movesegment(T_fifth_segment_timeout, T_accelerating_fifth_segment, 0, full_forward, straight, slow_forward, straight)
        #second Left turn
        self.movesegment(T_left_turn_time, T_accelerating_second_segment, 0, Stopped, full_left, straight, slow_forward)
        #return to start
        self.movesegment(T_last_segment_timeout, T_accelerating_last_segment, front_line_sensor, full_forward, straight, slow_forward, straight)
        #Enter start box
        self.movesegment(T_finish_timeout, T_accelerating_box_segment, rear_line_sensor, slow_forward, straight, Stopped, straight)
        # Final set motors to neutral to stop
        self.drive.set_neutral()

    def move_segment(
        self,
        total_timeout=0,
        accelerating_time=0,
        line_sensor=None,
        peak_throttle=0,
        peak_steering=0,
        end_throttle=0,
        end_steering=0
    ):
        #Note Line_sensor=0 if no line sensor exit required
        # calculate timeout times
        now = datetime.now()
        end_timeout = now + timedelta(seconds=total_timeout)
        acceleration_timeout = now + timedelta(seconds=accelerating_time)

        while now < end_timeout:
            # If we have a line sensor, check it here. Bail if necesary
            if line_sensor and (self.adc.read_voltage(line_sensor) > self.red_min):
                break

            if now < acceleration_timeout:
                #
                # What is the throttle variable in the ease_throttle call supposed to be here?
                #
                throttle = self.ease_throttle(throttle, peak_throttle, self.max_rate)
                steering = peak_steering
            else:
                # easing needs adding
                throttle = end_throttle
                steering = end_steering

            self.drive.mix_channels_and_assign(throttle, steering)

        # must have got better than usual acceleration.
        # need to slow down before finishing
        if throttle != end_throttle or steering != end_steering:
            # needs easing adding
            throttle = end_throttle
            # needs easing adding
            steering = end_steering
            self.drive.mix_channels_and_assign(throttle, steering)

    def ease_throttle(self, current_throttle, target, rate):
        now = datetime.now()
        # if variable is above target
        if current_throttle > target:
            new_throttle = max(target, current_throttle - rate * (now - last_throttle_update))
        # or variable is below target
        if current_throttle >= target:
            new_throttle = max(target, current_throttle + rate * (now - last_throttle_update))
        last_throttle_update = datetime.now()
        return new_throttle

    def ease_steering(self, current_steering, target, rate):
        now = datetime.now()
        # if variable is above target
        if current_steering > target:
            new_steering = max(target, current_steering - rate * (now - last_steering_update))
        # or variable is below target
        if current_steering >= target:
            new_steering = max(target, current_steering + rate * (now - last_steering_update))
        last_steering_update = datetime.now()
        return new_steering
