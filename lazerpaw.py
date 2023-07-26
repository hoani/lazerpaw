from controller.controller import Controller
from controller.vision import ThresholdProcessor
import cv2 as cv
import numpy as np
import server.server as server
from threading import Lock
from hardware.camera import Camera
from hardware.servo import PanTilt
from hardware.lazer import Lazer

class ControlRoutine:
    def __init__(self, pan, tilt, pan_boundary, tilt_boundary):
        self.mu = Lock()
        self.c = Controller(pan, tilt, pan_boundary, tilt_boundary)
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
        
        deltaPitch = self.pitchRange*((y - h/2))/h
        deltaYaw = self.yawRange*(-(x - w/2))/w
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

    pantilt = PanTilt()
    camera = Camera()
    lazer = Lazer()
    
    c = ControlRoutine(pantilt.get_pan(), pantilt.get_tilt(), pantilt.get_pan_boundary(), pantilt.get_tilt_boundary())
    server.set_start_cb(c.start)
    server.set_stop_cb(c.stop)

    lazerTester = LazerTester()
    server.set_lazer_tester_cb(lazerTester.set)

    shutdown = Shutdown()
    server.set_shutdown_cb(shutdown.set)

    threshold = ThresholdProcessor()
    server.set_threshold_cb(threshold.set_threshold)

    manual = ManualMode(camera.hfov*180/np.pi, camera.vfov*180/np.pi)
    server.set_manual_enabled_cb(manual.set_enabled)
    server.set_manual_command_cb(manual.set_cmd)

    dt = 0.05 ## TODO: make this more dynamic

    i = 0
    for capture in camera.frame():
        if shutdown.get():
            # TODO: make shutdown
            break

        masked = threshold.process_frame(capture)
        server.update_video(capture)
        server.update_proc(masked)

        ctl = c.update(masked, dt)
        if ctl is not None:
            lazer.set(ctl.lazer())

            pantilt.pan(ctl.yaw())
            pantilt.tilt(ctl.pitch())
        else:
            if manual.get_enabled():
                pantilt.increment_pan(manual.get_delta_yaw())
                pantilt.increment_tilt(manual.get_delta_pitch())
            lazer.set(lazerTester.get())

        pantilt.update(dt)
    
    camera.release()
    exit(0)