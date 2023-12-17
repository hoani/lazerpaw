from time import sleep
import numpy as np

class ServoControl:
    def __init__(self, servo, slewrate = 180/4):
        self.servo = servo
        self.slewrate = slewrate # deg/s
        self.target = self.servo.angle
        self.last = self.servo.angle

    def set_angle(self, angle):
        if angle < self.servo.min_angle:
            angle = self.servo.min_angle
        if angle > self.servo.max_angle:
            angle = self.servo.max_angle

        self.target = angle

    def get_angle(self):
        return self.last

    def increment(self, delta):
        self.set_angle(self.target + delta)

    def update(self, dt):
        slew = self.slewrate * dt
        delta = self.target - self.last
        if delta != 0:
            if np.abs(delta) < slew:
                self.last = self.target
            else:
                self.last += np.sign(delta) * slew
        else:
            self.last = self.target

        self.servo.angle = self.last

    def disable(self):
        self.servo.angle = None

    def boundary(self):
        return (self.servo.min_angle, self.servo.max_angle)

class PanTilt:
    def __init__(self, pan, tilt):
        self._pan = pan
        self._tilt = tilt

    def update(self, dt):
        self._pan.update(dt)
        self._tilt.update(dt)

    def disable(self):
        self._pan.disable()
        self._tilt.disable()

    def pan(self, angle):
        self._pan.set_angle(angle)

    def tilt(self, angle):
        self._tilt.set_angle(angle)

    def get_pan(self):
        return self._pan.get_angle()

    def get_tilt(self):
        return self._tilt.get_angle()

    def increment_pan(self, delta):
        self._pan.increment(delta)

    def increment_tilt(self, delta):
        self._tilt.increment(delta)

    def get_pan_boundary(self):
        return self._pan.boundary()

    def get_tilt_boundary(self):
        return self._tilt.boundary()

