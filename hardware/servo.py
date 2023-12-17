from gpiozero import AngularServo
from gpiozero.pins.pigpio import PiGPIOFactory
from time import sleep
import numpy as np

def Factory():
    return PiGPIOFactory()

def YawServo(factory):
    return AngularServo(
        18, 
        initial_angle=0, 
        min_angle=-50, 
        max_angle=50, 
        min_pulse_width=0.820/1000, 
        max_pulse_width=1.960/1000,
        pin_factory=factory)

def PitchServo(factory):
    return AngularServo(
        13, 
        initial_angle=10, 
        min_angle=5, 
        max_angle=50, 
        min_pulse_width=1.05/1000, 
        max_pulse_width=1.75/1000,
        pin_factory=factory)

if __name__ == "__main__":
    from ..controller.pantilt import PanTilt, ServoControl

    factory = PiGPIOFactory()
    yawCtl = ServoControl(YawServo(factory))
    pitchCtl = ServoControl(PitchServo(factory))
    pantilt = PanTilt(yawCtl, pitchCtl)

    deltaT = 0.2
    deltaAngle = 0.125
    sleep(1)

    while True:
        while pantilt.get_pan() < pantilt.get_pan_boundary()[1] - 0.5:
            pantilt.increment_pan(deltaAngle)
            pantilt.update(deltaT)
            sleep(deltaT)
        while pantilt.get_tilt() < pantilt.get_tilt_boundary()[1] - 0.5:
            pantilt.increment_tilt(deltaAngle)
            pantilt.update(deltaT)
            sleep(deltaT)
        while pantilt.get_pan() > pantilt.get_pan_boundary()[0] + 0.5:
            pantilt.increment_pan(-deltaAngle)
            pantilt.update(deltaT)
            sleep(deltaT)
        while pantilt.get_tilt() > pantilt.get_tilt_boundary()[0] + 0.5:
            pantilt.increment_tilt(-deltaAngle)
            pantilt.update(deltaT)
            sleep(deltaT)