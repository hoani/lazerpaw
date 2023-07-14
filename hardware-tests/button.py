from gpiozero import AngularServo,Button
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
		initial_angle=0, 
		min_angle=-45, 
		max_angle=0, 
		min_pulse_width=1.25/1000, 
		max_pulse_width=1.5/1000,
		pin_factory=factory)

factory = PiGPIOFactory()
servo1 = NewYawServo(factory)
servo2 = NewPitchServo(factory)

button = Button(27)

while True:
	servo1.min()
	servo2.mid()
	sleep(1)
	if button.is_pressed:
		servo1.mid()
	sleep(1)
