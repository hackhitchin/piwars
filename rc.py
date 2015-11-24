#!/usr/bin/env python
import sys
import cwiid
import logging
import time
import drivetrain
from wiimote import Wiimote, WiimoteException

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
        #drive = drivetrain.DriveTrain(pwm_i2c=0x41)
        #wiimote = None
        #try:
        #    wiimote = Wiimote()

        #except WiimoteException:
        #    logging.error("Could not connect to wiimote. please try again")
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

#if __name__ == "__main__":
#    try:
#        run()
#    except Exception as e:
#        logging.error("Stopping...")
#        logging.exception(e)
