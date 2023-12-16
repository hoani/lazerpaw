from controller.controller import Controller
from threading import Lock
import time, math


class ControlRoutine:
    ExecutionPeriod = 120

    def __init__(self, pantilt):
        self.mu = Lock()
        self.c = Controller(pantilt)
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
    Timeout = 60.0  # Manual mode expires if there has been no activity for 60 seconds.

    def __init__(self, pitchRange, yawRange):
        self.mu = Lock()
        self.enabled = False
        self.deltaPitch = 0
        self.deltaYaw = 0
        self.pitchRange = pitchRange
        self.yawRange = yawRange
        self.lastUpdated = time.time()

    def set_enabled(self, enabled):
        self.mu.acquire()
        self.enabled = enabled
        self.lastUpdated = time.time()
        self.mu.release()

    def set_cmd(self, x, y, w, h):
        if not self.get_enabled():
            return

        if w == 0 or h == 0:
            return

        deltaPitch = self.pitchRange * ((y - h / 2)) / h
        deltaYaw = self.yawRange * (-(x - w / 2)) / w
        print("setting delta pitch", deltaPitch, "delta yaw", deltaYaw)
        self.mu.acquire()
        self.lastUpdated = time.time()
        self.deltaPitch = deltaPitch
        self.deltaYaw = deltaYaw
        self.mu.release()

    def get_enabled(self):
        now = time.time()
        self.mu.acquire()
        if now - self.lastUpdated > __class__.Timeout:
            self.enabled = False

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


class SpecialMode:
    TARGET_X = 40
    TARGET_Y = 40
    MAX_DX = 1
    MAX_DY = 1
    ARRIVED_DX = 0.25
    ARRIVED_DY = 0.25
    MODE_TIMEOUT = 3600  # One hour.

    def __init__(self):
        self.lazer_count = 0
        self.arrived = False
        self.enabled = False

    def toggle_enable(self):
        if self.enabled:
            self.disable()
        else:
            self.enable()

    def enable(self):
        self.enabled = True

    def disable(self):
        if self.lazer_count > 60:  # Just to avoid debounce.
            self.enabled = False
            self.lazer_count = 0

    def get_enabled(self):
        result = self.enabled
        return result

    def get_deltas(self, x, y):
        if not self.enabled:
            return 0, 0

        dx, dy = self.get_distances(x, y)
        dx = max(-__class__.MAX_DX, min(dx, __class__.MAX_DX))
        dy = max(-__class__.MAX_DY, min(dy, __class__.MAX_DY))

        if dx < __class__.ARRIVED_DX and dy < __class__.ARRIVED_DY:
            self.arrived = True

        return dx, dy

    def get_lazer(self):
        if self.arrived:
            self.lazer_count += 1
            if (self.lazer_count % 60) < 30:
                return True
            if self.lazer_count > 30 * __class__.MODE_TIMEOUT:
                self.disable()
        return False

    def get_distances(self, x, y):
        dx = __class__.TARGET_X - x
        dy = __class__.TARGET_Y - y
        return dx, dy


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
