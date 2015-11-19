#!/usr/bin/env python
import cwiid
import time
from libs.Adafruit_PWM_Servo_Driver import PWM
from numpy import interp, clip

# activate the servos
SERVO_LEFT_CHANNEL = 0
SERVO_RIGHT_CHANNEL = 1
SERVO_MIN = 670
SERVO_MAX = 1870
SERVO_MID = 1270

class rc:
    def __init__(self):
        # Configure PWM
        self.pwm = PWM(0x40, debug=False)
        self.pwm.setPWMFreq(50)
        self.wm = None

    def set_servo_pulse(self, channel, pulse):
        # 1,000,000 us per second
        pulseLength = 1000000
        #  60 Hz
        pulseLength /= 50
        # 12 bits of resolution
        pulseLength /= 4096
        pulse /= pulseLength
        self.pwm.setPWM(channel, 0, pulse)

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

    def rc_neutral(self):
        # Set the servos to middle position
        self.set_servo_pulse(SERVO_LEFT_CHANNEL, SERVO_MID)
        self.set_servo_pulse(SERVO_RIGHT_CHANNEL, SERVO_MID)

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
                self.set_servo_pulse(SERVO_LEFT_CHANNEL, SERVO_MIN)
                self.set_servo_pulse(SERVO_RIGHT_CHANNEL, SERVO_MIN)
            elif (buttons & cwiid.BTN_2):
                # Button 2 pressed
                print("max")
                self.set_servo_pulse(SERVO_LEFT_CHANNEL, SERVO_MAX)
                self.set_servo_pulse(SERVO_RIGHT_CHANNEL, SERVO_MAX)
            elif (buttons & cwiid.BTN_A):
                # Button A pressed
                print("A")
            elif (buttons & cwiid.BTN_B):
                # Button B pressed
                print("stop")
                self.rc_neutral()
            elif (nunchuk_buttons & cwiid.NUNCHUK_BTN_C):
                # Button C pressed
                print("C")
            elif (nunchuk_buttons & cwiid.NUNCHUK_BTN_Z):
                # Button Z pressed
                print("stop")
                self.rc_neutral()
            else:
                acc_throttle = clip(self.wm.state['nunchuk']['stick'][1], 50, 200)
                pulse_throttle = int(
                    interp(
                        acc_throttle,
                        [50, 200],
                        [SERVO_MIN, SERVO_MAX]
                    )
                )
                acc_steering = clip(self.wm.state['nunchuk']['stick'][0], 50, 200)
                pulse_steering = int(
                    interp(
                        acc_steering,
                        [50, 200],
                        [SERVO_MIN, SERVO_MAX]
                    )
                )

                output_pulse_left = clip(
                    (-pulse_throttle + pulse_steering) / 2 + SERVO_MID,
                    SERVO_MIN,
                    SERVO_MAX
                )
                output_pulse_right = clip(
                    (pulse_throttle + pulse_steering) / 2,
                    SERVO_MIN,
                    SERVO_MAX
                )
                print "stick position: {0}, {1}".format(acc_throttle, pulse_throttle)
                print "output pulse left: {0} output pulse right : {1}".format(output_pulse_left, output_pulse_right)
                self.set_servo_pulse(SERVO_LEFT_CHANNEL, output_pulse_left)
                self.set_servo_pulse(SERVO_RIGHT_CHANNEL, output_pulse_right)

            time.sleep(0.05)

if  __name__ =='__main__':
    rc_control = rc()
    rc_control.rc_loop()
