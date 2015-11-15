#!/usr/bin/env python
import cwiid
import time
from libs.Adafruit_PWM_Servo_Driver import PWM
from numpy import interp, clip

# connecting to the wiimote. This allows several attempts
# as first few often fail.
pwm = PWM(0x40, debug=False)
pwm.setPWMFreq(50)


def set_servo_pulse(channel, pulse):
    # 1,000,000 us per second
    pulseLength = 1000000
    #  60 Hz
    pulseLength /= 50
    # 12 bits of resolution
    pulseLength /= 4096
    pulse /= pulseLength
    pwm.setPWM(channel, 0, pulse)

print("Press 1+2 on your Wiimote now...")
wm = None
i = 2
while not wm:
    try:
        wm = cwiid.Wiimote()
    except RuntimeError:
        if i > 5:
            print("cannot create connection")
            quit()
        print "Error opening wiimote connection"
        print "attempt " + str(i)
        i += 1

#set wiimote to report button presses and accelerometer state
wm.rpt_mode = cwiid.RPT_BTN | cwiid.RPT_ACC | cwiid.RPT_EXT

#turn on led to show connected
wm.led = 1

#activate the servos
SERVO_LEFT_CHANNEL = 0
SERVO_RIGHT_CHANNEL = 1
SERVO_MIN = 670
SERVO_MAX = 1870
SERVO_MID = 1270

while True:
    print wm.state
    buttons = wm.state['buttons']
    if 'nunchuk' not in wm.state:
        print('no nunchuk found - continuing')
    elif (buttons & cwiid.BTN_1):
        print("min")
        set_servo_pulse(SERVO_LEFT_CHANNEL, SERVO_MIN)
        set_servo_pulse(SERVO_RIGHT_CHANNEL, SERVO_MIN)
    elif (buttons & cwiid.BTN_2):
        print("max")
        set_servo_pulse(SERVO_LEFT_CHANNEL, SERVO_MAX)
        set_servo_pulse(SERVO_RIGHT_CHANNEL, SERVO_MAX)
    elif (buttons & cwiid.BTN_B):
        print("stop")
        set_servo_pulse(SERVO_LEFT_CHANNEL, SERVO_MID)
        set_servo_pulse(SERVO_RIGHT_CHANNEL, SERVO_MID)
    else:
        acc_throttle = clip(wm.state['nunchuk']['stick'][1], 50, 200)
        pulse_throttle = int(
            interp(
                acc_throttle,
                [50, 200],
                [SERVO_MIN, SERVO_MAX]
            )
        )
        acc_steering = clip(wm.state['nunchuk']['stick'][0], 50, 200)
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
        set_servo_pulse(SERVO_LEFT_CHANNEL, output_pulse_left)
        set_servo_pulse(SERVO_RIGHT_CHANNEL, output_pulse_right)

    time.sleep(0.05)
