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
        initial_angle=-90, 
        min_angle=-90, 
        max_angle=0, 
        min_pulse_width=1/1000, 
        max_pulse_width=1.5/1000,
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
        slew = self.slewRate * dt
        delta = self.target - self.servo.angle
        if delta != 0:
            if np.abs(delta) < slew:
                self.servo.angle = self.target
            else:
                self.servo.angle += np.sign(delta) * slew

class PanTilt:
    def __init__(self, slewrate = 180/2):
        factory = PiGPIOFactory()
        self.yaw = Control(YawServo(factory), slewrate)
        self.pitch = Control(PitchServo(factory), slewrate)

    def update(self, dt):
        self.pan.update(dt)
        self.tilt.update(dt)

    def pan(self, angle):
        self.pan.angle(angle)

    def tilt(self, angle):
        self.tilt.angle(angle)

    def increment_pan(self, delta):
        self.pan.increment(delta)

    def increment_tilt(self, delta):
        self.tilt.increment(delta)

if __name__ == "__main__":
    pantilt = PanTilt()

    deltaT = 0.1
    while True:
        while pantilt.yaw.angle < pantilt.yaw.max_angle:
            pantilt.increment_pan(1)
            pantilt.update(deltaT)
            sleep(deltaT)
        while pantilt.pitch.angle < pantilt.pitch.max_angle:
            pantilt.increment_tilt(1)
            pantilt.update(deltaT)
            sleep(deltaT)
        while pantilt.yaw.angle > pantilt.yaw.min_angle:
            pantilt.increment_pan(-1)
            pantilt.update(deltaT)
            sleep(deltaT)
        while pantilt.pitch.angle > pantilt.pitch.min_angle:
            pantilt.increment_tilt(-1)
            pantilt.update(deltaT)
            sleep(deltaT)