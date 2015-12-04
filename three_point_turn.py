# Three point turn pseudo code
#!/usr/bin/python
# -*- coding: utf-8 -*-

from ABE_ADCPi import ADCPi
from ABE_helpers import ABEHelpers
from datetime import datetime, timedelta
import sys
import logging
import time

logging.basicConfig(stream=sys.stdout, level=logging.INFO)


class ThreePointTurn:
    def __init__(self, drive):
        """ Standard Constructor """
        logging.info("Three Point Turn constructor")
        # set up ADC
        self.i2c_helper = ABEHelpers()
        self.bus = self.i2c_helper.get_smbus()
        self.adc = ADCPi(self.bus, 0x6a, 0x6b, 12)

        # define fixed values
        # red is typically 3.5V
        self.red_min = 3
        self.red = 3.5
        self.stopped = 0
        self.full_forward = 0.5
        self.half_forward = 0.25
        self.slow_forward = 0.1
        self.full_reverse = -0.5
        self.half_reverse = -0.25
        self.slow_reverse = -0.1

        self.straight = 0
        self.full_left = -1
        self.slow_left = -0.5
        self.rear_line_sensor = 2
        # same sensor for now
        self.front_line_sensor = 2
        self.max_rate = 2

        # Drivetrain is passed in
        self.drive = drive

        self.killed = False

    def run(self):
        """ Main call to run the three point turn script """
        # initiate camera

        # initialise throttle to 0
        # forward to turning point
        logging.info("forward to turning point")
        self.move_segment(
            total_timeout=0.6,
            line_sensor=self.rear_line_sensor,
            throttle=self.full_forward,
            steering=self.straight
        )
        # required slow speed braking
        logging.info("appling break")
        self.move_segment(
            total_timeout=0.4,
            line_sensor=self.rear_line_sensor,
            throttle=self.slow_forward,
            steering=self.straight
        )
        # required slow speed braking
        logging.info("aggressive break")
        self.move_segment(
            total_timeout=0.25,
            line_sensor=self.rear_line_sensor,
            throttle=self.half_reverse,
            steering=self.straight
        )
        # first left turn
        logging.info("first left turn")
        self.move_segment(
            total_timeout=0.1,
            throttle=self.stopped,
            steering=self.full_left
         )
        # Slow left turn (braking)
        #logging.info("first left turn")
        #self.move_segment(
        #    total_timeout=0.2,
        #    throttle=self.stopped,
        #    steering=self.slow_left
        # )
        # forward to first side line
        logging.info("forward to first side line")
        throttle = self.move_segment(
            total_timeout=0.2,
            line_sensor=self.front_line_sensor,
            throttle=self.full_forward,
            steering=self.straight
        )
        # required slow speed braking
        #logging.info("appling break")
        #self.move_segment(
        #    total_timeout=0.1,
        #    line_sensor=self.rear_line_sensor,
        #    throttle=self.slow_forward,
        #    steering=self.straight
        #)
        # reverse portion to second side line
        logging.info("reverse to second side line")
        throttle = self.move_segment(
            total_timeout=0.5,
            line_sensor=self.rear_line_sensor,
            throttle=self.full_reverse,
            steering=self.straight
        )
        # required slow speed braking
        logging.info("appling break")
        self.move_segment(
            total_timeout=0.1,
            line_sensor=self.rear_line_sensor,
            throttle=self.slow_forward,
            steering=self.straight
        )

        # required slow speed braking
        #logging.info("appling break")
        #self.move_segment(
        #    total_timeout=0.1,
        #    line_sensor=self.rear_line_sensor,
        #    throttle=self.slow_reverse,
        #    steering=self.straight
        #)
        # throttle = self.move_segment(
        #     total_timeout=0.75,
        #     accelerating_time=0.3,
        #     line_sensor=self.rear_line_sensor,
        #     max_throttle=self.
        #     full_reverse,
        #     max_steering=self.
        #     straight,
        #     end_throttle=self.
        #     slow_reverse,
        #     end_steering=self.
        #     straight,
        #     start_throttle=throttle
        # )
        # # reverse portion to second side line
        # throttle = self.move_segment(
        #     total_timeout=0.4,
        #     accelerating_time=0.2,
        #     max_throttle=self.full_forward,
        #     max_steering=self.straight,
        #     end_throttle=self.slow_forward,
        #     end_steering=self.straight,
        #     start_throttle=throttle
        # )
        # # second left turn
        # throttle = self.move_segment(
        #     total_timeout=0.3,
        #     accelerating_time=0.15,
        #     max_throttle=self.stopped,
        #     max_steering=self.full_left,
        #     end_throttle=self.straight,
        #     end_steering=self.slow_forward,
        #     start_throttle=throttle
        # )
        # # return to start
        # throttle = self.move_segment(
        #     total_timeout=0.35,
        #     accelerating_time=0.35,
        #     line_sensor=self.front_line_sensor,
        #     max_throttle=self.full_forward,
        #     max_steering=self.straight,
        #     end_throttle=self.slow_forward,
        #     end_steering=self.straight
        # )
        # # enter start box
        # throttle = self.move_segment(
        #     total_timeout=0.4,
        #     accelerating_time=0.2,
        #     line_sensor=self.rear_line_sensor,
        #     max_throttle=self.slow_forward,
        #     max_steering=self.straight,
        #     end_throttle=self.stopped,
        #     end_steering=self.straight
        # )
        # Final set motors to neutral to stop
        self.drive.set_neutral()
        self.stop()

    def stop(self):
        """Simple method to stop the challenge"""
        self.killed = True

    def move_segment(
        self,
        total_timeout=0,
        line_sensor=None,
        throttle=0,
        steering=0
    ):
        logging.info("move_segment called with arguments: {0}".format(locals()))
        # Note Line_sensor=0 if no line sensor exit required
        # calculate timeout times
        now = datetime.now()
        end_timeout = now + timedelta(seconds=total_timeout)

        last_throttle_update = None

        while not self.killed and (datetime.now() < end_timeout):
            logging.info("mixing channels: {0} : {1}".format(throttle, steering))
            # Swapped steering/throttle
            self.drive.mix_channels_and_assign(steering, throttle)
            # If we have a line sensor, check it here. Bail if necesary
            if line_sensor and (self.adc.read_voltage(line_sensor) > self.red_min):
                logging.info("Line Detected")
                break

            # if now < acceleration_timeout:
            #     throttle, last_throttle_update = self.ease_value(
            #         start_throttle,
            #         max_throttle,
            #         self.max_rate,
            #         last_throttle_update
            #     )
            #     steering = max_steering
            # else:
            #     # easing needs adding
            #     throttle = end_throttle
            #     steering = end_steering
            time.sleep(0.05)

        logging.info("Finished manoeuvre")
        # must have got better than usual acceleration.
        # need to slow down before finishing
        # if throttle != end_throttle or steering != end_steering:
        #     # needs easing adding
        #     throttle = end_throttle
        #     # needs easing adding
        #     steering = end_steering
        #     self.drive.mix_channels_and_assign(throttle, steering)
        return throttle

    def ease_value(self, current_value, target, rate, last_update_time=None):
        now = datetime.now()
        if last_update_time is None:
            last_update_time = now
        # if variable is above target
        if current_value > target:
            new_value = max(
                target, current_value - rate * int((now - last_update_time).total_seconds())
            )
        # or variable is below target
        if current_value <= target:
            new_value = max(
                target, current_value + rate * int((now - last_update_time).total_seconds())
            )
        last_update_time = datetime.now()
        return new_value, last_update_time
