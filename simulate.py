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

    def get(self):
        state = False
        if self.mu.acquire(timeout=dt):
            state = self.state
            self.mu.release()
        
        return state
    
    def set(self, state):
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

class ManualMode:
    def __init__(self, pitchRange, yawRange):
        self.mu = Lock()
        self.enabled = False
        self.deltaPitch = 0
        self.deltaYaw = 0
        self.pitchRange = pitchRange
        self.yawRange = yawRange

    def set_enabled(self, enabled):
        self.mu.acquire()
        self.enabled = enabled
        self.mu.release()
    
    def set_cmd(self, x, y, w, h):
        if not self.get_enabled():
            return
        
        if w == 0 or h == 0:
            return
        
        deltaPitch = self.pitchRange*(x - w/2)/w
        deltaYaw = self.yawRange*(-(y - h/2))/h
        print("setting delta pitch", deltaPitch, "delta yaw", deltaYaw)
        self.mu.acquire()
        self.deltaPitch = deltaPitch
        self.deltaYaw = deltaYaw
        self.mu.release()

    def get_enabled(self):
        self.mu.acquire()
        result = self.enabled
        self.mu.release()
        return result

    def get_delta_pitch(self):
        self.mu.acquire()
        result = self.deltaPitch
        self.deltaPitch = 0
        self.mu.release()
        return result
    
    def get_delta_yaw(self):
        self.mu.acquire()
        result = self.deltaYaw
        self.deltaYaw = 0
        self.mu.release()
        return result

class Shutdown:
    def __init__(self):
        self.mu = Lock()
        self.value = False

    def get(self):
        value = False
        if self.mu.acquire(timeout=dt):
            value = self.value
            self.mu.release()
        
        return value
    
    def set(self):
        self.mu.acquire()
        self.value = True
        self.mu.release()


if __name__ == "__main__":
    serverThread = server.start()

    room = Room()
    camera = Camera()
    sim = Simulation(room=room, camera=camera)
    sim.add_cat(Cat(randint(0, room.size[0]),randint(0, room.size[1])))
    
    c = ControlRoutine(camera.phi*180/np.pi, camera.theta*180/np.pi)
    server.set_start_cb(c.start)
    server.set_stop_cb(c.stop)

    lazerTester = LazerTester()
    server.set_lazer_tester_cb(lazerTester.set)

    shutdown = Shutdown()
    server.set_shutdown_cb(shutdown.set)

    threshold = Threshold()
    server.set_threshold_cb(threshold.set)

    manual = ManualMode(camera.hfov, camera.vfov)
    server.set_manual_enabled_cb(manual.set_enabled)
    server.set_manual_command_cb(manual.set_cmd)

    dt = 0.05

    while shutdown.get() is False:
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

            camera.commandPan(ctl.yaw() *np.pi/180)
            camera.commandTilt(ctl.pitch()*np.pi/180)
        else:
            if manual.get_enabled():
                camera.increment_pan(manual.get_delta_pitch())
                camera.increment_tilt(manual.get_delta_yaw())
            sim.lazerOn = lazerTester.get()

        if cv.waitKey(int(100*dt)) != -1:
            break

    exit(0)