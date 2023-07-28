from controller.controller import Controller
from threading import Lock
import time


class ControlRoutine:
    ExecutionPeriod = 120 
    def __init__(self, pan, tilt, pan_boundary, tilt_boundary):
        self.mu = Lock()
        self.c = Controller(pan, tilt, pan_boundary, tilt_boundary)
        self.running = False
        self.execution_start = time.time()

    def update(self, masked, dt):        
        if self.get_remaining() > 0:
            self.c.update(masked, dt)
            return self.c
            
        return None

    def get_remaining(self):
        self.mu.acquire()
        if self.running:
            delta = time.time() - self.execution_start
            remaining = ControlRoutine.ExecutionPeriod - delta
            if remaining < 0:
                remaining = 0
                self.running = False
        else:
            remaining = 0

        self.mu.release()
        return remaining

    def get_running(self):
        self.mu.acquire()
        value = self.running
        self.mu.release()
        return value
    
    def start(self):
        self.mu.acquire()
        self.running = True
        self.execution_start = time.time()
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
        self.mu.acquire()
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
        self.mu.acquire()
        value = self.value
        self.mu.release()
        
        return value
    
    def set(self):
        self.mu.acquire()
        self.value = True
        self.mu.release()