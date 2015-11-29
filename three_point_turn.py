# Three point turn pseudo code
#!/usr/bin/python
# -*- coding: utf-8 -*-

from ABE_ADCPi import ADCPi
from ABE_helpers import ABEHelpers
from datetime import datetime, timedelta


class ThreePointTurn:
    def __init__(self, drive):
        """ Standard Constructor """
        # set up ADC
        self.i2c_helper = ABEHelpers()
        self.bus = self.i2c_helper.get_smbus()
        self.adc = ADCPi(self.bus, 0x68, 0x69, 12)

        # define fixed values
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

        # initialise throttle to 0
        throttle = 0
        # forward to turning point
        throttle = self.move_segment(
            total_timeout=0.95,
            accelerating_time=0.5,
            line_sensor=self.rear_line_sensor,
            peak_throttle=self.full_forward,
            peak_steering=self.straight,
            end_throttle=self.slow_forward,
            end_steering=self.straight,
            start_throttle=throttle
        )
        # first left turn
        throttle = self.move_segment(
            total_timeout=0.3,
            accelerating_time=0.15,
            peak_throttle=self.stopped,
            peak_steering=self.full_left,
            end_throttle=self.straight,
            end_steering=self.slow_forward,
            start_throttle=throttle
        )
        # forward to first side line
        throttle = self.move_segment(
            total_timeout=0.4,
            accelerating_time=0.2,
            line_sensor=self.front_line_sensor,
            peak_throttle=self.full_forward,
            peak_steering=self.straight,
            end_throttle=self.slow_forward,
            end_steering=self.straight,
            start_throttle=throttle
        )
        # reverse portion to second side line
        throttle = self.move_segment(
            total_timeout=0.75,
            accelerating_time=0.3,
            line_sensor=self.rear_line_sensor,
            peak_throttle=self.
            full_reverse,
            peak_steering=self.
            straight,
            end_throttle=self.
            slow_reverse,
            end_steering=self.
            straight,
            start_throttle=throttle
        )
        # reverse portion to second side line
        throttle = self.move_segment(
            total_timeout=0.4,
            accelerating_time=0.2,
            peak_throttle=self.full_forward,
            peak_steering=self.straight,
            end_throttle=self.slow_forward,
            end_steering=self.straight,
            start_throttle=throttle
        )
        # second left turn
        throttle = self.move_segment(
            total_timeout=0.3,
            accelerating_time=0.15,
            peak_throttle=self.stopped,
            peak_steering=self.full_left,
            end_throttle=self.straight,
            end_steering=self.slow_forward,
            start_throttle=throttle
        )
        # return to start
        throttle = self.move_segment(
            total_timeout=0.35,
            accelerating_time=0.35,
            line_sensor=self.front_line_sensor,
            peak_throttle=self.full_forward,
            peak_steering=self.straight,
            end_throttle=self.slow_forward,
            end_steering=self.straight
        )
        # enter start box
        throttle = self.move_segment(
            total_timeout=0.4,
            accelerating_time=0.2,
            line_sensor=self.rear_line_sensor,
            peak_throttle=self.slow_forward,
            peak_steering=self.straight,
            end_throttle=self.stopped,
            end_steering=self.straight
        )
        # Final set motors to neutral to stop
        self.drive.set_neutral()

    def move_segment(
        self,
        total_timeout=0,
        accelerating_time=0,
        line_sensor=None,
        peak_throttle=0,
        peak_steering=0,
        start_throttle=0,
        end_throttle=0,
        end_steering=0
    ):
        # Note Line_sensor=0 if no line sensor exit required
        # calculate timeout times
        now = datetime.now()
        end_timeout = now + timedelta(seconds=total_timeout)
        acceleration_timeout = now + timedelta(seconds=accelerating_time)

        last_throttle_update = None

        while now < end_timeout:
            # If we have a line sensor, check it here. Bail if necesary
            if line_sensor and (self.adc.read_voltage(line_sensor) > self.red_min):
                break

            if now < acceleration_timeout:
                throttle, last_throttle_update = self.ease_value(throttle, peak_throttle, self.max_rate, last_throttle_update)
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
        return throttle

    def ease_value(self, current_value, target, rate, last_update_time=None):
        now = datetime.now()
        if last_update_time is None:
            last_update_time = now
        # if variable is above target
        if current_value > target:
            new_value = max(target, current_value - rate * (now - last_update_time))
        # or variable is below target
        if current_value >= target:
            new_value = max(target, current_value + rate * (now - last_update_time))
        last_update_time = datetime.now()
        return new_value, last_update_time
