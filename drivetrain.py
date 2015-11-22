import logging
from libs.Adafruit_PWM_Servo_Driver import PWM
from numpy import interp, clip


class DriveTrain():
    def __init__(
        self,
        pwm_i2c=0x40,
        pwm_freq=50,
        left_channel=0,
        right_channel=1,
        debug=False
    ):
        self.servo_min = 960
        self.servo_mid = 1270
        self.servo_max = 1870

        self.channels = {
            'left': left_channel,
            'right': right_channel
        }

        self.pwm = PWM(pwm_i2c, debug=debug)
        self.pwm.setPWMFreq(pwm_freq)

    def set_servo_pulse(self, channel, pulse):
        # 1,000,000 us per second
        pulseLength = 1000000
        #  60 Hz
        pulseLength /= 50
        logging.debug("%d us per period" % pulseLength)
        # 12 bits of resolution
        pulseLength /= 4096
        logging.debug("%d us per bit" % pulseLength)
        # pulse *= 1000
        pulse /= pulseLength
        logging.debug("pulse {0}".format(pulse))
        self.pwm.setPWM(channel, 0, pulse)

    def set_neutral(self):
        self.set_servo_pulse(self.channels['left'], self.servo_mid)
        self.set_servo_pulse(self.channels['right'], self.servo_mid)

    # TODO - flesh out setters for raw pulse values (both channels)
    def mix_channels(self, pulse_throttle, pulse_steering):
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

    def map_channel_value(self, value, min_max_range):
        return int(
            interp(
                value,
                min_max_range,
                [self.servo_min, self.servo_max]
            )
        )
