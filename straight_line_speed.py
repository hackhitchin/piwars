# Three point turn pseudo code
#!/usr/bin/python
# -*- coding: utf-8 -*-

from ABE_ADCPi import ADCPi
from ABE_helpers import ABEHelpers
from datetime import datetime, timedelta
import sys
import logging
import time
from numpy import interp, clip

logging.basicConfig(stream=sys.stdout, level=logging.INFO)


class StraightLineSpeed:
    def __init__(self, drive):
        """ Standard Constructor """
        logging.info("Straight Line Speed constructor")
        # set up ADC
        self.i2c_helper = ABEHelpers()
        self.bus = self.i2c_helper.get_smbus()
        self.adc = ADCPi(self.bus, 0x6a, 0x6b, 12)

        # define fixed values
        self.stopped = 0
        self.full_forward = 1
        self.slow_forward = 0.1
        self.full_reverse = -0.5
        self.slow_reverse = -0.1

        self.left_steering = -0.1
        self.right_steering = 0.1
        self.straight = 0.05
        self.distance_sensor = 1

        # Voltage value we are aiming for (2 was close, 0.5 was further away)
        self.nominal_distance = 45.0
        self.distance_range_min = -20.0
        self.distance_range_max = 20.0

        # Drivetrain is passed in
        self.drive = drive
        self.killed = False

    def stop(self):
        """Simple method to stop the challenge"""
        self.killed = True

    def run(self):
        """ Main call to run the three point turn script """
        # Drive forward for a set number of seconds keeping distance equal
        logging.info("forward to turning point")
        self.move_segment(total_timeout=2.0)

        # Final set motors to neutral to stop
        self.drive.set_neutral()
        self.stop()

    def move_segment(self, total_timeout=0):
        logging.info("move_segment called with arguments: {0}".format(locals()))
        # Note Line_sensor=0 if no line sensor exit required
        # calculate timeout times
        now = datetime.now()
        end_timeout = now + timedelta(seconds=total_timeout)

        # Throttle is static and does not change
        throttle = self.full_forward
        # Steering starts at zero (straight forward)
        steering = self.straight

        while not self.killed and (datetime.now() < end_timeout):
            # If we have a line sensor, check it here. Bail if necesary
            #if self.distance_sensor:
            #    voltage = self.adc.read_voltage(self.distance_sensor)
            #    # Distance calculation (units = cm)
            #    distance = 27.0/voltage
            #    distance_dif = distance - self.nominal_distance
            #
            #    steering = clip(
            #        interp(
            #            distance_dif,
            #            [self.distance_range_min, self.distance_range_max]
            #            [self.left_steering, self.right_steering],
            #        ),
            #        self.left_steering,
            #        self.right_steering
            #    )
            time.sleep(0.05)

            # Had to invert throttle and steering channels to match RC mode
            logging.info("mixing channels: {0} : {1}".format(throttle, steering))
            self.drive.mix_channels_and_assign(steering, throttle)

        logging.info("Finished manoeuvre")
