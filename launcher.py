#!/usr/bin/env python
import os
import sys
import cwiid
import logging
import time
import drivetrain
from wiimote import Wiimote, WiimoteException
from Adafruit_CharLCD import Adafruit_CharLCD
import threading
import rc
from three_point_turn import ThreePointTurn
from proximity import Proximity
from line_following import LineFollowing
from straight_line_speed import StraightLineSpeed
import RPi.GPIO as GPIO


logging.basicConfig(stream=sys.stdout, level=logging.INFO)


class launcher:
    def __init__(self):
        # Need a state set for this launcher.
        self.menu = ["Remote Control"]
        self.menu += ["Three Point Turn"]
        self.menu += ["Straight Line Speed"]
        self.menu += ["Line Following"]
        self.menu += ["Proximity"]
        self.menu += ["Quit Challenge"]
        self.menu += ["Power Off Pi"]

        self.menu_quit_challenge = 3

        # default menu item is remote control
        self.menu_state = 0
        self.menu_button_pressed = False
        self.drive = None
        self.wiimote = None
        # Current Challenge
        self.challenge = None
        self.challenge_name = ""

        GPIO.setwarnings(False)
        self.GPIO = GPIO

        # LCD Display
        self.lcd = Adafruit_CharLCD( pin_rs=25, pin_e=24, pins_db=[23, 17, 27, 22], GPIO=self.GPIO )
        self.lcd.begin(16, 1)
        self.lcd.clear()
        self.lcd.message('Initiating...')
        self.lcd_loop_skip = 5
        # Shutting down status
        self.shutting_down = False

    def menu_item_selected(self):
        """Select the current menu item"""
        # If ANYTHING selected, we gracefully
        # kill any challenge threads open
        self.stop_threads()
        if self.menu[self.menu_state]=="Remote Control":
            # Start the remote control
            logging.info("Entering into Remote Control Mode")
            self.challenge = rc.rc(self.drive, self.wiimote)
            # Create and start a new thread running the remote control script
            self.challenge_thread = threading.Thread(target=self.challenge.run)
            self.challenge_thread.start()
            # Ensure we know what challenge is running
            if self.challenge:
                self.challenge_name = self.menu[self.menu_state]
            # Move menu index to quit challenge by default
            self.menu_state = self.menu_quit_challenge
        elif self.menu[self.menu_state]=="Three Point Turn":
            # Start the three point turn challenge
            logging.info("Starting Three Point Turn Challenge")
            self.challenge = ThreePointTurn(self.drive)
            # Create and start a new thread running the remote control script
            self.challenge_thread = threading.Thread(target=self.challenge.run)
            self.challenge_thread.start()
            # Ensure we know what challenge is running
            if self.challenge:
                self.challenge_name = self.menu[self.menu_state]
            # Move menu index to quit challenge by default
            self.menu_state = self.menu_quit_challenge
        elif self.menu[self.menu_state]=="Straight Line Speed":
            # Start the straight line speed challenge
            logging.info("Starting Straight Line Speed Challenge")
            self.challenge = StraightLineSpeed(self.drive)
            # Ensure we know what challenge is running
            if self.challenge:
                self.challenge_name = self.menu[self.menu_state]
            # Move menu index to quit challenge by default
            self.menu_state = self.menu_quit_challenge
        elif self.menu[self.menu_state]=="Line Following":
            # Start the Line Following challenge
            logging.info("Starting Line Following Challenge")
            self.challenge = LineFollowing(self.drive)
            # Ensure we know what challenge is running
            if self.challenge:
                self.challenge_name = self.menu[self.menu_state]
            # Move menu index to quit challenge by default
            self.menu_state = self.menu_quit_challenge
        elif self.menu[self.menu_state]=="Proximity":
            # Start the Proximity challenge
            logging.info("Starting Proximity Challenge")
            self.challenge = Proximity(self.drive)
            # Ensure we know what challenge is running
            if self.challenge:
                self.challenge_name = self.menu[self.menu_state]
            # Move menu index to quit challenge by default
            self.menu_state = self.menu_quit_challenge        
        elif self.menu[self.menu_state]=="Quit Challenge":
            # Reset menu item back to top of list
            self.menu_state = 0
            logging.info("No Challenge Challenge Thread")
        elif self.menu[self.menu_state]=="Power Off Pi":
            # Power off the raspberry pi safely
            # by sending shutdown command to terminal
            logging.info("Shutting Down Pi")
            os.system("sudo shutdown -h now")
            self.shutting_down = True

    def set_neutral(self, drive, wiimote):
        """Simple method to ensure motors are disabled"""
        if drive:
            drive.set_neutral()
            drive.disable_drive()
        if wiimote is not None:
            # turn on leds on wii remote
            wiimote.led = 2

    def set_drive(self, drive, wiimote):
        """Simple method to highlight that motors are enabled"""
        if wiimote is not None:
            # turn on leds on wii remote
            #turn on led to show connected
            drive.enable_drive()
            wiimote.led = 1

    def stop_threads(self):
        """Method neatly closes any open threads started by this class"""
        if self.challenge:
            self.challenge.stop()
            self.challenge = None
            self.challenge_thread = None
            logging.info("Stopping Challenge Thread")
        else:
            logging.info("No Challenge Challenge Thread")
        # Safety setting
        self.set_neutral(self.drive, self.wiimote)

    def run(self):
        """ Main Running loop controling bot mode and menu state """
        # Tell user how to connect wiimote
        self.lcd.clear()
        self.lcd.message( 'Press 1+2 \n' )
        self.lcd.message( 'On Wiimote' )

        # Initiate the drivetrain
        self.drive = drivetrain.DriveTrain(pwm_i2c=0x40)
        self.wiimote = None
        try:
            self.wiimote = Wiimote()

        except WiimoteException:
            logging.error("Could not connect to wiimote. please try again")

        if not self.wiimote:
            # Tell user how to connect wiimote
            self.lcd.clear()
            self.lcd.message( 'Wiimote \n' )
            self.lcd.message( 'Not Found' + '\n' )

        # Constantly check wiimote for button presses
        loop_count = 0
        while self.wiimote:
            buttons_state = self.wiimote.get_buttons()
            nunchuk_buttons_state = self.wiimote.get_nunchuk_buttons()
            joystick_state = self.wiimote.get_joystick_state()

#            logging.info("joystick_state: {0}".format(joystick_state))
#            logging.info("button state {0}".format(buttons_state))
            # Always show current menu item
            # logging.info("Menu: " + self.menu[self.menu_state])

            if loop_count >= self.lcd_loop_skip:
                # Reset loop count if over
                loop_count = 0

                self.lcd.clear()
                if self.shutting_down:
                    # How current menu item on LCD
                    self.lcd.message( 'Shutting Down Pi' + '\n' )
                else:
                    # How current menu item on LCD
                    self.lcd.message( self.menu[self.menu_state] + '\n' )

                    # If challenge is running, show it on line 2
                    if self.challenge:
                        self.lcd.message( '[' + self.challenge_name + ']' )

            # Increment Loop Count
            loop_count = loop_count + 1

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
                    self.menu_state = self.menu_state - 1
                    if self.menu_state < 0:
                        # Loop back to end of list
                        self.menu_state = len(self.menu)-1
                    logging.info("Menu item: {0}".format(self.menu[self.menu_state]))
                elif not self.menu_button_pressed and (buttons_state & cwiid.BTN_DOWN):
                    # Increment menu index
                    self.menu_state = self.menu_state + 1
                    if self.menu_state >= len(self.menu):
                        # Loop back to start of list
                        self.menu_state = 0
                    logging.info("Menu item: {0}".format(self.menu[self.menu_state]))

                # Only change button state AFTER we have used it
                self.menu_button_pressed = True
            else:
                # No menu buttons pressed
                self.menu_button_pressed = False

            time.sleep(0.05)

if __name__ == "__main__":
    launcher = launcher()
    try:
        launcher.run()
    except (Exception, KeyboardInterrupt) as e:
        # Stop any active threads before leaving
        launcher.stop_threads()
        logging.error("Stopping...")
        logging.exception(e)
