# Three point turn pseudo code
#!/usr/bin/python
# -*- coding: utf-8 -*-

from ABE_ADCPi import ADCPi
from ABE_helpers import ABEHelpers
import sys
import logging
import time

logging.basicConfig(stream=sys.stdout, level=logging.INFO)


class Proximity:
    def __init__(self, drive):
        """ Standard Constructor """
        logging.info("Proximity constructor")
        # set up ADC
        self.i2c_helper = ABEHelpers()
        self.bus = self.i2c_helper.get_smbus()
        self.adc = ADCPi(self.bus, 0x6a, 0x6b, 12)

        # define fixed values
        self.stopped = 0
        self.full_forward = 0.4
        self.slow_forward = 0.3
        self.full_reverse = -0.5
        self.slow_reverse = -0.25

        self.left_steering = -0.25
        self.right_steering = 0.25
        self.straight = 0
        self.distance_sensor = 1

        # Voltage value we are aiming for (2 was close, 0.5 was further away)
        self.distance_threshold = 50.0
        self.distance_required = 17.0

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
        self.move_segment()

        # Final set motors to neutral to stop
        logging.info("Finished Event")
        self.drive.set_neutral()

    def get_distance(self):
        distance = 0.0
        if self.distance_sensor:
            voltage = self.adc.read_voltage(self.distance_sensor)
            distance = 27.0 / voltage
        return distance

    def move_segment(self):
        logging.info("move_segment called with arguments: {0}".format(locals()))

        # Throttle is static and does not change
        throttle = self.full_forward
        # Steering starts at zero (straight forward)
        steering = self.straight

        # Drive forward at half speed until we get reasonably close
        distance = self.get_distance()
        logging.info("Entering Full Speed")

        logging.info("distance: {0}".format(distance))
        time.sleep(0.05)
        while not self.killed and (distance > self.distance_threshold):
            self.drive.mix_channels_and_assign(self.straight, self.full_forward)
            distance = self.get_distance()
            logging.info("F: distance: {0}".format(distance))
            time.sleep(0.05)

        self.drive.set_neutral()
        time.sleep(0.05)
        logging.info("Entering Half Speed")

        # Drive forward at slow/min speed until we get very close
        while not self.killed and (distance > self.distance_required):
            self.drive.mix_channels_and_assign(self.straight, self.slow_forward)
            distance = self.get_distance()
            logging.info("S: distance: {0}".format(distance))
            time.sleep(0.05)

        # Ever so slight brake
        self.drive.mix_channels_and_assign(self.straight, self.slow_reverse)
        time.sleep(0.05)
        self.drive.set_neutral()
        time.sleep(0.05)
        logging.info("Finished manoeuvre")
