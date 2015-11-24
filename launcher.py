#!/usr/bin/env python
import os
import sys
import cwiid
import logging
import time
import drivetrain
from wiimote import Wiimote, WiimoteException

import threading
import rc

class launcher:
    def __init__(self):
        # Need a state set for this launcher.
        self.menu = ["Remote Control"]
        self.menu += ["Three Point Turn"]
        self.menu += ["Straight Line Speed"]
        self.menu += ["Quit Challenge"]
        self.menu += ["Power Off Pi"]

        # default menu item is remote control
        self.menu_state = 0
        self.menu_button_pressed = False
        self.drive = None
        self.wiimote = None
        # Current Challenge
        self.challenge = None

    def menu_item_selected(self):
        """Select the current menu item"""
        if self.menu[self.menu_state]=="Remote Control":
            # Start the remote control
            logging.info("Entering into Remote Control Mode")
            self.challenge = rc.rc(self.drive, self.wiimote)
            # Create and start a new thread running the remote control script
            self.challenge_thread = threading.Thread(target=self.challenge.run)
            self.challenge_thread.start()
        elif self.menu[self.menu_state]=="Three Point Turn":
            # Start the three point turn challenge
            logging.info("Starting Three Point Turn Challenge")
            self.challenge = None
        elif self.menu[self.menu_state]=="Straight Line Speed":
            # Start the straight line speed challenge
            logging.info("Starting Straight Line Speed Challenge")
            self.challenge = None
        elif self.menu[self.menu_state]=="Quit Challenge":
            # Gracefully kill any challenge thread
            if self.challenge:
                self.challenge.stop()
                self.challenge = None
                self.challenge_thread = None
                logging.info("Stopping Challenge Thread")
                # Reset menu item back to top of list
                self.menu_state = 0
            else:
                logging.info("No Challenge Challenge Thread")
        elif self.menu[self.menu_state]=="Power Off Pi":
            # Power off the raspberry pi safely 
            # by sending shutdown command to terminal
            logging.info("Shutting Down Pi")
            os.system("sudo shutdown -h now")

    def set_neutral(self, drive, wiimote):
        """Simple method to ensure motors are disabled"""
        if drive:
            drive.set_neutral()
            drive.disable_drive()
        if wiimote != None:
            # turn on leds on wii remote
            wiimote.led = 2

    def set_drive(self, drive, wiimote):
        """Simple method to highlight that motors are enabled"""
        if wiimote != None:
            # turn on leds on wii remote
            #turn on led to show connected
            drive.enable_drive()
            wiimote.led = 1

    def run(self):
        # Set up logging
        logging.basicConfig(stream=sys.stdout, level=logging.INFO)
        # Initiate the drivetrain
        self.drive = drivetrain.DriveTrain(pwm_i2c=0x41)
        self.wiimote = None
        try:
            self.wiimote = Wiimote()

        except WiimoteException:
            logging.error("Could not connect to wiimote. please try again")

        # Constantly check wiimote for button presses
        while self.wiimote:
            buttons_state = self.wiimote.get_buttons()
            nunchuk_buttons_state = self.wiimote.get_nunchuk_buttons()
            joystick_state = self.wiimote.get_joystick_state()

#            logging.info("joystick_state: {0}".format(joystick_state))
#            logging.info("button state {0}".format(buttons_state))
            # Always show current menu item
            logging.info("Menu: " + self.menu[self.menu_state])

            # Test if B button is pressed
            if joystick_state is None or (buttons_state & cwiid.BTN_B) or (nunchuk_buttons_state & cwiid.NUNCHUK_BTN_Z):
                # No nunchuk joystick detected or B or Z button 
                # pressed, must go into neutral for safety
                logging.info("Neutral")
                self.set_neutral(self.drive, self.wiimote)
            else:
                # Enable motors
                self.set_drive(self.drive, self.wiimote)
                if ((buttons_state & cwiid.BTN_A)
                    or (buttons_state & cwiid.BTN_UP) 
                    or (buttons_state & cwiid.BTN_DOWN)):
                    # Looking for state change only
                    if not self.menu_button_pressed and (buttons_state & cwiid.BTN_A):
                        # User wants to select a menu item
                        self.menu_item_selected()
                    elif not self.menu_button_pressed and (buttons_state & cwiid.BTN_UP):
                        # Decrement menu index
                        logging.info("Menu Down Pressed")
                        self.menu_state = self.menu_state - 1
                        if self.menu_state < 0:
                            # Loop back to end of list
                            self.menu_state = len(self.menu)-1
#                        logging.info(self.menu[self.menu_state])
                    elif not self.menu_button_pressed and (buttons_state & cwiid.BTN_DOWN):
                        # Increment menu index
                        logging.info("Menu Up Pressed")
                        self.menu_state = self.menu_state + 1
                        if self.menu_state >= len(self.menu):
                            # Loop back to start of list
                            self.menu_state = 0
#                        logging.info(self.menu[self.menu_state])

                    # Only change button state AFTER we have used it
                    self.menu_button_pressed = True
                else:
                    # No menu buttons pressed
                    self.menu_button_pressed = False

            time.sleep(0.05)

if __name__ == "__main__":
    try:
        launcher = launcher()
        launcher.run()
    except Exception as e:
        logging.error("Stopping...")
        logging.exception(e)
