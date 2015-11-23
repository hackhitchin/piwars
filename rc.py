#!/usr/bin/env python
import sys
import cwiid
import logging
import time
import drivetrain
from wiimote import Wiimote, WiimoteException
import argparse


def run(i2c=None):
    # Set up logging
    logging.basicConfig(stream=sys.stdout, level=logging.INFO)
    # Initiate the drivetrain
    drive = drivetrain.DriveTrain(pwm_i2c=0x4 if i2c is None else i2c)
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
            # Get the normalised joystick postion as a tuple of
            # (throttle, steering), where values are in the range -1 to 1
            joystick_pos = joystick_state['state']['normalised']
            throttle, steering = joystick_pos
            drive.mix_channels_and_assign(throttle, steering)

        time.sleep(0.05)

if __name__ == "__main__":
    def auto_int(x):
        return int(x, 0)
    parser = argparse.ArgumentParser(description='Radio Control TTOS.')
    parser.add_argument('--i2c', type=auto_int)
    args = parser.parse_args()
    try:
        i2c = args.i2c if args.i2c else None
        run()
    except Exception as e:
        logging.error("Stopping...")
        logging.exception(e)
