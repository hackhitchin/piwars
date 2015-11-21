#!/usr/bin/env python
import cwiid
import time
import motors
from numpy import interp, clip

class rc:
    def __init__(self, mc):
        # Initialise remote control class
        self.motors = mc
        self.wm = None

    def connect_wii_mote(self):
        # Connect to a waiting wii remote
        max_attempts = 5
        print("Press 1+2 on your Wiimote now...")
        self.wm = None
        i = 2
        while not self.wm:
            try:
                self.wm = cwiid.Wiimote()
            except RuntimeError:
                if i > max_attempts:
                    print("cannot create connection")
                    quit()
                print "Error opening wiimote connection"
                print "attempt " + str(i)
                i += 1

    def rc_loop(self):
        # Main loop that listens to the wii remote control
        # and enacts upon it.
        self.connect_wii_mote()
        if not self.wm:
            # Sanity checking that we connected
            return

        #set wiimote to report button presses and accelerometer state
        self.wm.rpt_mode = cwiid.RPT_BTN | cwiid.RPT_ACC | cwiid.RPT_EXT
        #turn on led to show connected
        self.wm.led = 1

        while True:
            print self.wm.state

            buttons = self.wm.state['buttons']
            nunchuk_buttons = None
            if 'nunchuk' in self.wm.state:
                nunchuk_buttons = self.wm.state['nunchuk']['buttons']

            if 'nunchuk' not in self.wm.state:
                # Check whether the nunchuk is connected
                print('no nunchuk found - continuing')
            elif (buttons & cwiid.BTN_1):
                # Button 1 pressed
                print("min")
                if self.motors:
                    self.motors.set_motor_speed(True, -100.0)
                    self.motors.set_motor_speed(False, -100.0)
            elif (buttons & cwiid.BTN_2):
                # Button 2 pressed
                print("max")
                if self.motors:
                    self.motors.set_motor_speed(True, 100.0)
                    self.motors.set_motor_speed(False, 100.0)
            elif (buttons & cwiid.BTN_A):
                # Button A pressed
                print("A")
            elif (buttons & cwiid.BTN_B):
                # Button B pressed
                print("stop")
                if self.motors:
                    self.motors.set_neutral()
            elif (nunchuk_buttons & cwiid.NUNCHUK_BTN_C):
                # Button C pressed
                print("C")
            elif (nunchuk_buttons & cwiid.NUNCHUK_BTN_Z):
                # Button Z pressed
                print("stop")
                if self.motors:
                    self.motors.set_neutral()
            else:
                # Get stick position
                stick_pos_throttle = clip(self.wm.state['nunchuk']['stick'][1], 50, 200)
                stick_pos_steering = clip(self.wm.state['nunchuk']['stick'][0], 50, 200)

                # joystick and motor power ranges
                min_stick_range = 50
                max_stick_range = 200;
                min_motor_range = -100.0
                max_motor_range = 100.0;

                # Convert stick position to range (-100, 100)
                throttle_scaled = int(
                    interp(
                        stick_pos_throttle,
                        [min_stick_range, max_stick_range],
                        [min_motor_range, max_motor_range]
                    )
                )
                # Convert stick position to range (-100, 100)
                steering_scaled = int(
                    interp(
                        stick_pos_steering,
                        [min_stick_range, max_stick_range],
                        [min_motor_range, max_motor_range]
                    )
                )

                # Clip the throttle and steering speeds to the range (-100, 100)
                #motor_left = clip( (-pulse_throttle + pulse_steering) / 2, -100.0, 100.0 )
                #motor_right = clip( (pulse_throttle + pulse_steering) / 2, -100.0, 100.0 )
                self.skid_steering(throttle_scaled, steering_scaled)

            time.sleep(0.05)

    def skid_steering(self, throttle_scaled, steering_scaled):
        # mix throttle and direction
        print "stick position: Throttle " + str(throttle_scaled) + ' Steering  ' + str(steering_scaled)
        motor_left =  clip((throttle_scaled + steering_scaled) / 2, -100.0, 100.0);
        motor_right = clip((throttle_scaled - steering_scaled) / 2, -100.0, 100.0);
        print "motor position: Left Motor " + str(motor_left) + ' Right Motor ' + str(motor_right)
        self.motors.set_motor_speed(True, motor_left)
        self.motors.set_motor_speed(False, motor_right)

if  __name__ =='__main__':
    mc = motors.motors()
    rc_control = rc(mc)
    rc_control.rc_loop()
