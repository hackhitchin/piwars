#!/usr/bin/env python
import sys
import cwiid
import logging
import time
import drivetrain
from wiimote import Wiimote, WiimoteException


def run():
    # Set up logging
    logging.basicConfig(stream=sys.stdout, level=logging.INFO)
    # Initiate the drivetrain
    drive = drivetrain.DriveTrain(pwm_i2c=0x41)
    wiimote = None
    try:
        wiimote = Wiimote()

    except WiimoteException:
        logging.error("Could not connect to wiimote. please try again")
    while wiimote:
        buttons_state = wiimote.get_buttons()
        joystick_state = wiimote.get_joystick_state()

        logging.info("joystick_state: {0}".format(joystick_state))
        logging.info("button state {0}".format(buttons_state))

        # Test if B button is pressed
        if joystick_state is None or (buttons_state & cwiid.BTN_B):
            logging.info("B button presed - stopping")
            drive.set_neutral()
        else:
            joystick_pos = joystick_state['state']['normalised']
            throttle, steering = joystick_pos
            drive.mix_channels(throttle, steering)

        time.sleep(0.05)

if __name__ == "__main__":
    try:
        run()
    except Exception as e:
        logging.error("Stopping...")
        logging.exception(e)
