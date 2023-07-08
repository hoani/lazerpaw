from gpiozero import Servo
from gpiozero.pins.pigpio import PiGPIOFactory
from time import sleep

factory = PiGPIOFactory()
servo1 = Servo(18, pin_factory=factory)
servo2 = Servo(13, pin_factory=factory)

while True:
	servo1.min()
	sleep(2)
	servo2.min()
	sleep(2)
	servo1.mid()
	sleep(2)
	servo2.mid()
	sleep(2)
	servo1.max()
	sleep(2)
	servo2.max()
	sleep(2)
