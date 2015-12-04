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


class line_test:
    def __init__(self):
        """ Standard Constructor """
        logging.info("Three Point Turn constructor")
        # set up ADC
        self.i2c_helper = ABEHelpers()
        self.bus = self.i2c_helper.get_smbus()
        self.adc = ADCPi(self.bus, 0x6a, 0x6b, 12)

        self.killed = False

    def run(self, line_sensor=None):
        logging.info("Started Looking")

        while not self.killed:
            # If we have a line sensor, check it here. Bail if necesary
            #if line_sensor and (self.adc.read_voltage(line_sensor) > self.red_min):
            #    logging.info("Line Detected")
            if line_sensor:
                logging.info( str(self.adc.read_voltage(line_sensor)) )
            time.sleep(0.05)

lt = line_test()
#channel 1 == distance sensor
#channel 2 == line sensor
channel = 1
lt.run( channel )
