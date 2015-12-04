#!/usr/bin/env python
import logging
import time
import cwiid


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
        # Initiate the drivetrain
        while self.wiimote and not self.killed:
            buttons_state = self.wiimote.get_buttons()
            nunchuk_buttons_state = self.wiimote.get_nunchuk_buttons()
            joystick_state = self.wiimote.get_joystick_state()

            #logging.debug("joystick_state: {0}".format(joystick_state))
            #logging.debug("button state {0}".format(buttons_state))

            # If 'C' is pressed, go to full speed
            if (nunchuk_buttons_state & cwiid.NUNCHUK_BTN_C):
                self.drive.set_full_speed()
            else:
                self.drive.set_low_speed()

            # Get the normalised joystick postion as a tuple of
            # (throttle, steering), where values are in the range -1 to 1
            joystick_pos = joystick_state['state']['normalised']
            throttle, steering = joystick_pos
            logging.info("mixing channels: {0} : {1}".format(throttle, steering))
            self.drive.mix_channels_and_assign(throttle, steering)

            time.sleep(0.05)
        # Final thing we do leaving RC mode is to 
        # set back into neutral for safety
        if self.drive:
            self.drive.set_neutral()