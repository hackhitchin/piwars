from __future__ import division
import logging
from libs.Adafruit_PWM_Servo_Driver import PWM
from numpy import interp, clip


class DriveTrain():
    """Instantiate a 2WD drivetrain, utilising 2x ESCs,
    controlled using a 2 axis (throttle, steering) system"""
    def __init__(
        self,
        pwm_i2c=0x40,
        pwm_freq=50,
        left_channel=0,
        right_channel=1,
        debug=False
    ):
        self.servo_min = 670
        self.servo_mid = 1270
        self.servo_max = 1870

        self.channels = {
            'left': left_channel,
            'right': right_channel
        }

        self.pwm = PWM(pwm_i2c, debug=debug)
        self.pwm.setPWMFreq(pwm_freq)
        # Flag set to True when motors are allowed to move
        self.drive_enabled = True

    def set_servo_pulse(self, channel, pulse):
        """Send a raw servo pulse length to a specific speed controller
        channel"""
        # Only send servo pulses if drive is enabled
        if self.drive_enabled:
            # 1,000,000 us per second
            pulseLength = 1000000
            #  60 Hz
            pulseLength /= 50
            # logging.debug("%d us per period" % pulseLength)
            # 12 bits of resolution
            pulseLength /= 4096
            # logging.debug("%d us per bit" % pulseLength)
            # pulse *= 1000
            pulse /= pulseLength
            logging.debug("pulse {0} - channel {1}".format(int(pulse), channel))
            self.pwm.setPWM(channel, 0, int(pulse))

    def enable_drive(self):
        """Allow motors to be used"""
        self.drive_enabled = True

    def disable_drive(self):
        """Disable motors so they cant be used"""
        self.set_neutral()
        self.drive_enabled = False

    def set_neutral(self):
        """Send the neutral servo position to both motor controllers"""
        self.set_servo_pulse(self.channels['left'], self.servo_mid)
        self.set_servo_pulse(self.channels['right'], self.servo_mid)

    # TODO - flesh out setters for raw pulse values (both channels)
    def mix_channels_and_assign(self, throttle, steering):
        """Take values for the throttle and steering channels in the range
        -1 to 1, convert into servo pulses, and then mix the channels and
        assign to the left/right motor controllers"""
        if not self.drive_enabled:
            return
        pulse_throttle = self._map_channel_value(throttle)
        pulse_steering = self._map_channel_value(steering)
        output_pulse_left = clip(
            (-pulse_throttle + pulse_steering) / 2 + self.servo_mid,
            self.servo_min,
            self.servo_max
        )
        output_pulse_right = clip(
            (pulse_throttle + pulse_steering) / 2,
            self.servo_min,
            self.servo_max
        )

        logging.info(
            "output pulse left: {0} output pulse right : {1}".format(
                output_pulse_left, output_pulse_right
            )
        )

        # Set the servo pulses for left and right channels
        self.set_servo_pulse(self.channels['left'], output_pulse_left)
        self.set_servo_pulse(self.channels['right'], output_pulse_right)

    def _map_channel_value(self, value):
        """Map the supplied value from the range -1 to 1 to a corresponding
        value within the range servo_min to servo_max"""
        return int(
            interp(
                value,
                [-1, 1],
                [self.servo_min, self.servo_max]
            )
        )
