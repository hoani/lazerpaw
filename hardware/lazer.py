from gpiozero import LED
from time import sleep

class Lazer(LED):
	def __init__(self):
		LED.__init__(self, 26)

if __name__ == "__main__":
	lazer = Lazer()
	while True:
		lazer.on()
		sleep(1)
		lazer.off()
		sleep(1)

