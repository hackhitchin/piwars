#!/usr/bin/env python
from libs.Adafruit_PWM_Servo_Driver import PWM

class motors:
    def __init__(self):
        # Servo parameters
        self.motor_channel_left = 0
        self.motor_channel_right = 0
        self.motor_range_min = 670
        self.motor_range_mid = 1270
        self.motor_range_max = 1870
        self.motor_range = self.motor_range_max - self.motor_range_min
        # Configure PWM
        self.pwm = PWM(0x40, debug=False)
        self.pwm.setPWMFreq(50)
        # 1,000,000 us per second
        self.pwm_pulseLength = 1000000
        #  60 Hz
        self.pwm_pulseLength /= 50
        # 12 bits of resolution
        self.pwm_pulseLength /= 4096

    def set_motor_pulse(self, channel, motor_value):
        # Set motor speed
        pulse = int(motor_value / self.pwm_pulseLength)
        self.pwm.setPWM(channel, 0, pulse)

    def set_motor_speed(self, left, speed):
        # Set left or right motor speed based (range -100 to 100)
        # Zero is garanteed to be neutral
        motor_speed = self.motor_range_mid # default speed to neutral position

        # Clip user input speed to min amd max range
        if speed < -100.0:
            speed = -100.0
        elif speed > 100.0:
            speed = 100.0
        # Only calculate motor speed if not in neutral position
        if speed!=0.0:
            motor_speed = self.motor_range_mid + ((speed / 200.0) * self.motor_range)
        # Convert left/right to motor channel
        motor_channel = self.motor_channel_left
        if not left:
            motor_channel = self.motor_channel_right
        # Send motor a pulse to set its speed
        self.set_motor_pulse(motor_channel, motor_speed)

    def set_neutral(self):
        # Set the servos to middle position
        self.set_motor_speed(True, 0)
        self.set_motor_speed(False, 0)
