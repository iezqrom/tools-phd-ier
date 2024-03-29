import time
import numpy as np
import os, sys

# https://github.com/m-lundberg/simple-pid/blob/30dd5460f484e866176c3a907c3421b515329867/simple_pid/PID.py#L130
# https://github.com/ivmech/ivPID/blob/master/PID.py


def clamp(value, limits):
    lower, upper = limits
    if value > upper:
        value = upper
    elif value < lower:
        value = lower

    return value


try:
    # get monotonic time to ensure that time deltas are always positive
    _current_time = time.monotonic
except AttributeError:
    # time.monotonic() not available (using python < 3.3), fallback to time.time()
    _current_time = time.time
    warnings.warn(
        "time.monotonic() not available in python < 3.3, using time.time() as fallback"
    )

# frame = 1


class PYD(object):
    def __init__(
        self,
        Kp,
        setpoint,
        Ki=0,
        Kd=0,
        gain_scheduling_range=None,
        output_limits=(None, None),
        sample_time=0.001,
    ):
        """
        :param Kp: The value for the proportional gain Kp
        :param Ki: The value for the integral gain Ki
        :param Kd: The value for the derivative gain Kd
        :param setpoint: The initial setpoint that the PID will try to achieve
        :param sample_time: The time in seconds which the controller should wait before generating a new output value.
                            The PID works best when it is constantly called (eg. during a loop), but with a sample
                            time set so that the time difference between each update is (close to) constant. If set to
                            None, the PID will compute a new output value every time it is called.
        :param output_limits: The initial output limits to use, given as an iterable with 2 elements, for example:
                                (lower, upper). The output will never go below the lower limit or above the upper limit.
                                Either of the limits can also be set to None to have no limit in that direction. Setting
                                output limits also avoids integral windup, since the integral term will never be allowed
                                to grow outside of the limits.

        """

        self.Kp, self.Ki, self.Kd = Kp, Ki, Kd
        self.setpoint = setpoint
        self.gain_scheduling_range = gain_scheduling_range

        self._min_output, self._max_output = output_limits
        self.output_limits = output_limits
        # print('output limits')
        # print(self.output_limits)
        # self.integral_limits = integral_limits
        self.sample_time = sample_time

        self._last_input = None

        self.proportional = 0
        self.integral = 0
        self.derivative = 0
        self._last_time = _current_time()

        self._last_output = None

    def run(self, present_input, dt=None):
        """
        Call the PID controller with *input* and calculate and return a control output if sample_time seconds has
        passed since the last update. If no new output is calculated, return the previous output instead (or None if
        no value has been calculated yet).
        :param dt: If set, uses this value for timestep instead of real time. This can be used in simulations when
                    simulation time is different from real time.
        """
        try:
            now = _current_time()
            if dt is None:
                dt = now - self._last_time if now - self._last_time else 1e-16
            elif dt <= 0:
                raise ValueError(
                    "dt has nonpositive value {}. Must be positive.".format(dt)
                )

            # print(dt)
            if (
                self.sample_time is not None
                and dt < self.sample_time
                and self._last_output is not None
            ):
                return self._last_output

            self.error = self.setpoint - present_input
            d_input = present_input - (
                self._last_input if self._last_input is not None else present_input
            )

            # compute proportional error
            self.proportional = self.Kp * self.error

            # compute integral and derivative terms
            if self.Ki != None:
                self.integral += self.Ki * self.error * dt
                # print('integral')
                # print(self.integral)
                self.integral = clamp(
                    self.integral, self.output_limits
                )  # avoid integral windup
            else:
                self.integral = 0

            if self.Kd != None:
                self.derivative = -self.Kd * d_input / dt
            else:
                self.derivative = 0

            # compute final output
            output = self.proportional + self.integral + self.derivative
            #    print('output: ' + str(output))
            output = clamp(output, self.output_limits)

            # keep track of state
            self._last_output = output
            self._last_input = present_input
            self._last_time = now

            self.output = output

        except Exception as e:
            print(e)
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(exc_type, fname, exc_tb.tb_lineno)

    def runGainSchedule(self, input, dt=None):
        """
        Call the PID controller with *input* and calculate and return a control output if sample_time seconds has
        passed since the last update. If no new output is calculated, return the previous output instead (or None if
        no value has been calculated yet).
        :param dt: If set, uses this value for timestep instead of real time. This can be used in simulations when
                    simulation time is different from real time.
        """

        now = _current_time()
        if dt is None:
            dt = now - self._last_time if now - self._last_time else 1e-16
        elif dt <= 0:
            raise ValueError(
                "dt has nonpositive value {}. Must be positive.".format(dt)
            )

        # print(dt)
        if (
            self.sample_time is not None
            and dt < self.sample_time
            and self._last_output is not None
        ):
            return self._last_output

        error = self.setpoint - input
        d_input = input - (self._last_input if self._last_input is not None else input)

        if input < 24:
            input = 24
        elif input > 33:
            input = 33

        schedule_pos = np.where(self.gain_scheduling_range == input)
        schedule_pos = schedule_pos[0][0]

        # compute proportional error
        self.proportional = self.Kp[schedule_pos] * error

        # compute integral and derivative terms
        self.integral += self.Ki[schedule_pos] * error * dt
        self.integral = clamp(
            self.integral, self.output_limits
        )  # avoid integral windup

        self.derivative = -self.Kd[schedule_pos] * d_input / dt

        # compute final output
        output = self.proportional + self.integral + self.derivative
        output = clamp(output, self.output_limits)

        # keep track of state
        self._last_output = output
        self._last_input = input
        self._last_time = now

        self.output = output

        self.current_Kp = self.Kp[schedule_pos]
        self.current_Kd = self.Kd[schedule_pos]
        self.current_Ki = self.Ki[schedule_pos]
