#!/usr/bin/env python
import cwiid
import time
from libs.Adafruit_PWM_Servo_Driver import PWM
from numpy import interp, clip

#connecting to the wiimote. This allows several attempts
# as first few often fail.
pwm = PWM(0x40, debug=False)
pwm.setPWMFreq(50)
#servos.setPWM(15,4095)

def set_servo_pulse(channel, pulse):
    pulseLength = 1000000 # 1,000,000 us per second
    pulseLength /= 50 #  60 Hz
    print "%d us per period" % pulseLength
    pulseLength /= 4096 # 12 bits of resolution
    print "%d us per bit" % pulseLength
    # pulse *= 1000
    pulse /= pulseLength
    print "pulse {0}".format(pulse)
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
#            servos.setPWM(15,0)
            quit()
        print "Error opening wiimote connection"
        print "attempt " + str(i)
        i += 1

#set wiimote to report button presses and accelerometer state
wm.rpt_mode = cwiid.RPT_BTN | cwiid.RPT_ACC

#turn on led to show connected
wm.led = 1

#activate the servos
# servos.setPWM(15,0)
# servos.setSpeeds(0,0)
#print state every second
SERVO_MIN = 900
SERVO_MAX = 2100
SERVO_MID = ((SERVO_MAX - SERVO_MIN) / 2) + SERVO_MIN

while True:
    # print wm.state
    buttons = wm.state['buttons']
    if (buttons & cwiid.BTN_1):
        print((wm.state['acc'][1]-125))
       # servos.setSpeeds((speedModifier - wm.state['acc'][1]),wm.state['acc'][1] -speedModifier2)
        # set_servo_pulse( (speedModifier - wm.state['acc'][1]),wm.state['acc'][1] -speedModifier2)
        set_servo_pulse(0, SERVO_MIN)
    elif (buttons & cwiid.BTN_2):
        print ~(wm.state['acc'][1]-125)
        #servos.setSpeeds(~(speedModifier - wm.state['acc'][1]),~(wm.state['acc'][1] -speedModifier2))
        # set_servo_pulse(~(speedModifier - wm.state['acc'][1]),~(wm.state['acc'][1] -speedModifier2))
        set_servo_pulse(0, SERVO_MAX)
    elif (buttons & cwiid.BTN_B):
        print("stop")
        set_servo_pulse(0, SERVO_MID)
    else:
        acc = clip(wm.state['acc'][1], 100, 150)
        pulse = int(interp(acc, [100, 150], [SERVO_MIN, SERVO_MAX]))
        set_servo_pulse(0, pulse)
    time.sleep(0.05)
