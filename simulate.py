from simulator.simulator import Room, Camera, Cat, Simulation
from controller.controller import Controller
import cv2 as cv
import numpy as np
from random import randint


if __name__ == "__main__":
    room = Room()
    camera = Camera()
    sim = Simulation(room=room, camera=camera)
    sim.addCat(Cat(randint(0, room.size[0]),randint(0, room.size[1])))

    c = Controller(camera.phi*180/np.pi, camera.theta*180/np.pi)

    dt = 0.05

    while True:
        capture = sim.update()
        capture = cv.resize(capture, (320,240))

        gray = cv.cvtColor(capture, cv.COLOR_BGR2GRAY)
        _, masked = cv.threshold(gray, 95, 255, cv.THRESH_BINARY)
        cv.imshow('masked', masked)


        c.update(masked, dt)
        sim.lazerOn = c.lazer()

        camera.commandPan(c.yaw())
        camera.commandTilt(c.pitch())

        if cv.waitKey(int(100*dt)) != -1:
            break

    exit(0)