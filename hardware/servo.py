from gpiozero import AngularServo
from gpiozero.pins.pigpio import PiGPIOFactory
from time import sleep
import numpy as np

def YawServo(factory):
    return AngularServo(
        18, 
        initial_angle=0, 
        min_angle=-45, 
        max_angle=45, 
        min_pulse_width=1.25/1000, 
        max_pulse_width=1.75/1000,
        pin_factory=factory)

def PitchServo(factory):
    return AngularServo(
        13, 
        initial_angle=0, 
        min_angle=0, 
        max_angle=40, 
        min_pulse_width=1.05/1000, 
        max_pulse_width=1.4/1000,
        pin_factory=factory)

class Control:
    def __init__(self, servo: AngularServo, slewrate = 180/2):
        self.servo = servo
        self.slewrate = slewrate # deg/s
        self.target = self.servo.angle

    def angle(self, angle):
        if angle < self.servo.min_angle:
            angle = self.servo.min_angle
        if angle > self.servo.max_angle:
            angle = self.servo.max_angle

        self.target = angle

    def increment(self, delta):
        self.angle(self.target + delta)

    def update(self, dt):
        slew = self.slewrate * dt
        delta = self.target - self.servo.angle
        if delta != 0:
            if np.abs(delta) < slew:
                self.servo.angle = self.target
            else:
                self.servo.angle += np.sign(delta) * slew

    def boundary(self):
        return (self.servo.min_angle, self.servo.max_angle)

class PanTilt:
    def __init__(self, slewrate = 180/2):
        factory = PiGPIOFactory()
        self.yaw = Control(YawServo(factory), slewrate)
        self.pitch = Control(PitchServo(factory), slewrate)

    def update(self, dt):
        self.yaw.update(dt)
        self.pitch.update(dt)

    def pan(self, angle):
        self.yaw.angle(angle)

    def tilt(self, angle):
        self.pitch.angle(angle)

    def get_pan(self):
        return self.yaw.servo.angle

    def get_tilt(self):
        return self.pitch.servo.angle

    def increment_pan(self, delta):
        self.yaw.increment(delta)

    def increment_tilt(self, delta):
        self.pitch.increment(delta)

    def get_pan_boundary(self):
        return self.yaw.boundary()

    def get_tilt_boundary(self):
        return self.pitch.boundary()

if __name__ == "__main__":
    pantilt = PanTilt()

    deltaT = 0.2
    deltaAngle = 0.125
    while True:
        while pantilt.yaw.servo.angle < pantilt.yaw.servo.max_angle - 0.5:
            pantilt.increment_pan(deltaAngle)
            pantilt.update(deltaT)
            sleep(deltaT)
        while pantilt.pitch.servo.angle < pantilt.pitch.servo.max_angle - 0.5:
            pantilt.increment_tilt(deltaAngle)
            pantilt.update(deltaT)
            sleep(deltaT)
        while pantilt.yaw.servo.angle > pantilt.yaw.servo.min_angle + 0.5:
            pantilt.increment_pan(-deltaAngle)
            pantilt.update(deltaT)
            sleep(deltaT)
        while pantilt.pitch.servo.angle > pantilt.pitch.servo.min_angle + 0.5:
            pantilt.increment_tilt(-deltaAngle)
            pantilt.update(deltaT)
            sleep(deltaT)