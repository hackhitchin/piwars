# Line Following code
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


class LineFollowing:
    def __init__(self, drive):
        """ Standard Constructor """
        logging.info("Line Following constructor")
        # set up ADC
        self.i2c_helper = ABEHelpers()
        self.bus = self.i2c_helper.get_smbus()
        self.adc = ADCPi(self.bus, 0x6a, 0x6b, 12)

        # define fixed values
        self.stopped = 0
        self.full_forward = 0.5
        self.slow_forward = 0.3
        self.full_reverse = -0.5
        self.slow_reverse = -0.1

        self.left_steering = -0.25
        self.right_steering = 0.25
        self.straight = 0

        # Voltage values we're dealing with
        self.black = 2.0
        self.white = 0.4

        # Drivetrain is passed in
        self.drive = drive
        self.killed = False

    def stop(self):
        """Simple method to stop the challenge"""
        self.killed = True

    def run(self):
        """ Main call to run the line following script """
        # Drive forward for a set number of seconds keeping distance equal
        logging.info("following line")
        self.move_segment(total_timeout=10.0)

        # Final set motors to neutral to stop
        self.drive.set_neutral()
        self.stop()

    def move_segment(self, total_timeout=0):
        # calculate timeout times
        now = datetime.now()
        end_timeout = now + timedelta(seconds=total_timeout)

        # Throttle is static and does not change
        throttle = self.full_forward
        # Steering starts at zero (straight forward)
        steering = self.straight

        while not self.killed and (datetime.now() < end_timeout):
            # steering is proportional to line sensor position
            steering = interp(
                self.get_line_position,
                [-3.5, 3.5]
                [self.left_steering, self.right_steering]
            )

            # Had to invert throttle and steering channels to match RC mode
            logging.info(
                "mixing channels: {0} : {1}".format(
                    throttle,
                    steering
                )
            )
            self.drive.mix_channels_and_assign(steering, throttle)
            time.sleep(0.05)

        logging.info("Finished manoeuvre")

    def get_line_position(self):
        """
        line_position = (-3.5 * v1 - 2.5 * v2 - 1.5 * v3 - 0.5 * v4 + 0.5 * v5 + 1.5 * v6 + 2.5 * v7 + 3.5 * v8 ) / (v1 + v2 + v3 + v4 + v5 + v6 + v7 + v8)
        """
        # get each line sensor value
        voltages = [
            self.adc.read_voltage(pin)
            for pin
            in range(1, 9)
        ]
        line_position = sum(
            [
                voltages[i] * (i - 3.5)
                for i
                in range(8)
            ]
        ) / sum(voltages)

        return line_position
