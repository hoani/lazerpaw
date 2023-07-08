from gpiozero import Servo,Button
from gpiozero.pins.pigpio import PiGPIOFactory
from time import sleep

factory = PiGPIOFactory()
servo1 = Servo(18, pin_factory=factory)
servo2 = Servo(13, pin_factory=factory)

button = Button(22)

while True:
	servo1.min()
	servo2.mid()
	sleep(1)
	if button.is_pressed:
		servo1.mid()
	sleep(1)
