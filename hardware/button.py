from gpiozero import Button
import time 

class Button:
	CommandNone = 0
	CommandRun = 1
	CommandShutdown = 2

	ShutdownHoldTime = 1.0

	def __init__(self):
		self.button = Button(27)
		self.lastState = False
		self.holdStart = time.time()

	def update(self):
		cmd = Button.CommandNone
		currentState = self.button.is_pressed
		if self.lastState != currentState:
			if self.button.is_pressed:
				self.holdStart = time.time()
			else:
				holdTime = time.time() - self.holdStart
				if holdTime > Button.ShutdownHoldTime:
					cmd = Button.CommandShutdown
				else:
					cmd = Button.CommandRun
		
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
