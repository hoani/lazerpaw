from simulator.simulator import Room, Camera, Cat, Simulation
from controller.controller import Controller
import cv2 as cv
import numpy as np
from random import randint
import server.server as server
from threading import Lock

class ControlRoutine:
    def __init__(self, phi, theta):
        self.mu = Lock()
        self.c = Controller(phi, theta)
        self.running = False

    def update(self, masked, dt):
        running = False
        if self.mu.acquire(timeout=dt):
            running = self.running
            self.mu.release()
        
        if running:
            self.c.update(masked, dt)
            return self.c
        return None
    
    def start(self):
        self.mu.acquire()
        self.running = True
        self.mu.release()
    
    def stop(self):
        self.mu.acquire()
        self.running = False
        self.mu.release()

class LazerTester:
    def __init__(self):
        self.mu = Lock()
        self.state = False

    def testState(self):
        state = False
        if self.mu.acquire(timeout=dt):
            state = self.state
            self.mu.release()
        
        return state
    
    def setState(self, state):
        self.mu.acquire()
        self.state = state
        self.mu.release()

class Threshold:
    def __init__(self):
        self.mu = Lock()
        self.value = 95

    def get(self):
        value = 95
        if self.mu.acquire(timeout=dt):
            value = self.value
            self.mu.release()
        
        return value
    
    def set(self, value):
        self.mu.acquire()
        self.value = value
        self.mu.release()

class Shutdown:
    def __init__(self):
        self.mu = Lock()
        self.state = False

    def getState(self):
        state = False
        if self.mu.acquire(timeout=dt):
            state = self.state
            self.mu.release()
        
        return state
    
    def shutdown(self):
        self.mu.acquire()
        self.state = True
        self.mu.release()


if __name__ == "__main__":
    serverThread = server.start()

    room = Room()
    camera = Camera()
    sim = Simulation(room=room, camera=camera)
    sim.addCat(Cat(randint(0, room.size[0]),randint(0, room.size[1])))
    
    c = ControlRoutine(camera.phi*180/np.pi, camera.theta*180/np.pi)
    server.set_start_cb(c.start)
    server.set_stop_cb(c.stop)

    lazerTester = LazerTester()
    server.set_lazer_tester_cb(lazerTester.setState)

    shutdown = Shutdown()
    server.set_shutdown_cb(shutdown.shutdown)

    threshold = Threshold()
    server.set_threshold_cb(threshold.set)

    dt = 0.05

    while shutdown.getState() is False:
        capture = sim.update()
        capture = cv.resize(capture, (640,480))

        server.update_video(capture)

        gray = cv.cvtColor(capture, cv.COLOR_BGR2GRAY)
        _, masked = cv.threshold(gray, threshold.get(), 255, cv.THRESH_BINARY)
        masked = cv.resize(masked, (320,240))

        server.update_proc(masked)


        ctl = c.update(masked, dt)
        if ctl is not None:
            sim.lazerOn = ctl.lazer()

            camera.commandPan(ctl.yaw())
            camera.commandTilt(ctl.pitch())
        else:
            sim.lazerOn = lazerTester.testState()

        if cv.waitKey(int(100*dt)) != -1:
            break

    exit(0)