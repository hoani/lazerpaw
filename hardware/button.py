from gpiozero import Button as GpioButton
import time 

class Button:
	CommandNone = 0
	CommandRun = 1
	CommandShutdown = 2

	ShutdownHoldTime = 1.0

	def __init__(self):
		self.button = GpioButton(27)
		self.lastState = False
		self.holdStart = time.time()
		self.issued = True

	def update(self):
		cmd = Button.CommandNone
		currentState = self.button.is_pressed
		if self.lastState != currentState:
			if self.button.is_pressed:
				self.holdStart = time.time()
				self.issued = False
			else:
				if self.issued == False:
					cmd = Button.CommandRun
		else:
			if self.button.is_pressed and self.issued == False:
				holdTime = time.time() - self.holdStart
				if holdTime > Button.ShutdownHoldTime:
					cmd = Button.CommandShutdown
					self.issued = True
		
		self.lastState = currentState
		return cmd

if __name__ == "__main__":
	button = Button()

	while True:
		cmd = button.update()
		if cmd == Button.CommandRun:
			print("run")
		elif cmd == Button.CommandShutdown:
			print("shutdown")
		time.sleep(1/30)
