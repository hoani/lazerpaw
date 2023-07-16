from gpiozero import AngularServo
from gpiozero.pins.pigpio import PiGPIOFactory
from time import sleep

def NewYawServo(factory):
    return AngularServo(
        18, 
        initial_angle=0, 
        min_angle=-45, 
        max_angle=45, 
        min_pulse_width=1.25/1000, 
        max_pulse_width=1.75/1000,
        pin_factory=factory)

def NewPitchServo(factory):
    return AngularServo(
        13, 
        initial_angle=-90, 
        min_angle=-90, 
        max_angle=0, 
        min_pulse_width=1/1000, 
        max_pulse_width=1.5/1000,
        pin_factory=factory)

if __name__ == "__main__":
    factory = PiGPIOFactory()
    servo1 = NewYawServo(factory)
    servo2 = NewPitchServo(factory)


    while True:
        
        while servo2.angle < servo2.max_angle:
            servo2.angle += 0.5
            sleep(1)
        while servo2.angle > servo2.min_angle:
            servo2.angle -= 0.5
            sleep(1)



