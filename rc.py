#!/usr/bin/env python
import sys
import logging
import time


class rc:
    def __init__(self, drive, wiimote):
        self.killed = False
        self.drive = drive
        self.wiimote = wiimote

    def stop(self):
        """Simple method to stop the RC loop"""
        self.killed = True

    def run(self):
        """Start listening to the wiimote and drive the motors"""
        # Set up logging
        logging.basicConfig(stream=sys.stdout, level=logging.INFO)
        # Initiate the drivetrain
        while self.wiimote and not self.killed:
            buttons_state = self.wiimote.get_buttons()
            joystick_state = self.wiimote.get_joystick_state()

            logging.info("joystick_state: {0}".format(joystick_state))
            logging.info("button state {0}".format(buttons_state))

            # Get the normalised joystick postion as a tuple of
            # (throttle, steering), where values are in the range -1 to 1
            joystick_pos = joystick_state['state']['normalised']
            throttle, steering = joystick_pos
            self.drive.mix_channels_and_assign(throttle, steering)

            time.sleep(0.05)
