from __future__ import division
import logging
from libs.Adafruit_PWM_Servo_Driver import PWM
from numpy import interp, clip


class DriveTrain():
    """Instantiate a 2WD drivetrain, utilising 2x ESCs,
    controlled using a 2 axis (throttle, steering) system + skittle accessories"""
    def __init__(
        self,
        pwm_i2c=0x40,
        pwm_freq=50,
        left_channel=0,
        right_channel=1,
        aux_channel1=4,
        aux_channel2=5,
        aux_channel3=6,
        aux_channel4=7,
        debug=False
    ):
        # Main set of motor controller ranges
        self.servo_min = 900
        #self.servo_mid = 1555
        self.servo_mid = 1650
        self.servo_max = 2300

        # Full speed range
        self.servo_full_min = 900
        self.servo_full_max = 2300
        # Low speed range is 1/4 of full speed
        speed_divisor = 2
        self.servo_low_min = int(self.servo_mid - (self.servo_mid-self.servo_full_min)/speed_divisor)
        self.servo_low_max = int(self.servo_mid + (self.servo_full_max-self.servo_mid)/speed_divisor)

        # Skittle launcher servos
        self.skittle_left_servo_closed = 1600
        self.skittle_left_servo_open = 1400
        self.skittle_right_servo_closed = 1600
        self.skittle_right_servo_open = 1400

        # Skittle launcher motors
        self.skittle_left_motor_stopped = 1000
        self.skittle_left_motor_full_speed = 2000
        self.skittle_left_motor_stopped = 1000
        self.skittle_left_motor_full_speed = 2000

        # Proximity probe servo limites
        self.proximity_servo_min = 1000
        self.proximity_servo_max = 2000

        # Proximity probe fan limits
        self.proximity_blower_esc_stopped = 1000
        self.proximity_blower_esc_max = 2000


        self.channels = {
            'left': left_channel,
            'right': right_channel
            'blower': aux_channel1
            'probe_servo': aux_channel2
            'skittle_left_servo':aux_channel1
            'skittle_right_servo':aux_channel2
            'skittle_left_motor':aux_channel3
            'skittle_right_motor':aux_channel4
        }

        self.pwm = PWM(pwm_i2c, debug=debug)
        self.pwm.setPWMFreq(pwm_freq)
        # Flag set to True when motors are allowed to move
        self.drive_enabled = False
        self.disable_drive()

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

    def set_full_speed(self):
        """Set servo range to FULL extents"""
        self.servo_min = self.servo_full_min
        self.servo_max = self.servo_full_max

    def set_low_speed(self):
        """Limit servo range extents"""
        self.servo_min = self.servo_low_min
        self.servo_max = self.servo_low_max

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
            #(-pulse_throttle + pulse_steering) / 2 + self.servo_mid,
            (pulse_throttle + pulse_steering) / 2,
            self.servo_min,
            self.servo_max
        )
        output_pulse_right = clip(
            #(pulse_throttle + pulse_steering) / 2,
            (pulse_throttle - pulse_steering) / 2 + self.servo_mid,
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
    def set_skittle_arms_closed(self):
        """Send the back servo position to both skittle servos"""
        self.set_servo_pulse(self.channels['skittle_left_servo'], self.skittle_left_servo_closed)
        self.set_servo_pulse(self.channels['skittle_right_servo'], self.skittle_right_servo_closed)

    def set_skittle_arms_open(self):
        """Send the forward servo position to both skittle servos"""
        self.set_servo_pulse(self.channels['skittle_left_servo'], self.skittle_left_servo_open)
        self.set_servo_pulse(self.channels['skittle_right_servo'], self.skittle_right_servo_open)

    def set_skittle_motors_on(self):
        """Send the on servo position to both skittle escs"""
        self.set_servo_pulse(self.channels['skittle_left_motor'], self.skittle_left_motor_full_speed)
        self.set_servo_pulse(self.channels['skittle_right_motor'], self.skittle_right_motor_full_speed)

    def set_skittle_motors_off(self):
        """Send the stopped servo position to both skittle escs"""
        self.set_servo_pulse(self.channels['skittle_left_motor'], self.skittle_left_motor_stopped)
        self.set_servo_pulse(self.channels['skittle_right_motor'], self.skittle_right_motor_stopped)