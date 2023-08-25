import cv2 as cv
import numpy as np
from threading import Lock
import time

def draw_crosshair(frame):
    xc, yc = int(frame.shape[1]/2), int(frame.shape[0]/2)
    c = 0,255,122
    cv.rectangle(frame, (xc-3, yc-3), (xc+2, yc+2), c, thickness=1)

class ThresholdProcessor:
    def __init__(self, panBoundary, tiltBoundary, fov = 48.8):
        self.mu = Lock()
        self.threshold = 95
        self.radius = 25
        self.fov = fov
        self.xb0, self.xb1 = panBoundary[0]-5, panBoundary[1]+5
        self.yb0, self.yb1 = tiltBoundary[0]-5, tiltBoundary[1]+5
        self.mask_x = None
        self.mask_y = None

    def apply_fov_boundary(self, masked, pan, tilt):
        if self.mask_x is None:
            self.mask_x = -pan
            self.mask_y = tilt
        else:
            # This basic filter is added because often the camera frame lags the servo commanded position.
            self.mask_x = -0.5 * pan + 0.5 * self.mask_x
            self.mask_y = 0.5 * tilt + 0.5 * self.mask_y

        w, h = masked.shape[1], masked.shape[0]
        ppdeg = w/self.fov
        xc, yc = w/2, h/2
        x, y = self.mask_x, self.mask_y
        x0, x1  = xc + (self.xb0 - x)*ppdeg, xc + (self.xb1 - x)*ppdeg
        y0, y1 = yc + (self.yb0 - y)*ppdeg, yc + (self.yb1 - y)*ppdeg

        masked = cv.rectangle(masked, (0, 0), (int(w), int(y0)), 0, thickness=cv.FILLED)
        masked = cv.rectangle(masked, (0, int(y0)), (int(x0), int(y1)), 0, thickness=cv.FILLED)
        masked = cv.rectangle(masked, (int(x1), int(y0)), (int(w), int(y1)), 0, thickness=cv.FILLED)
        masked = cv.rectangle(masked, (0, int(y1)), (int(w), int(h)), 0, thickness=cv.FILLED)
        
        return masked


    def process_frame(self, frame, pan, tilt):
        threshold = self.get_threshold()

        ## Note: It is slightly faster to resize, then threshold than the other way around.
        mono = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
        mono = cv.resize(mono, (80,60), cv.INTER_LINEAR)
        _, masked = cv.threshold(mono, threshold, 255, cv.THRESH_BINARY)

        ## Apply FOV boundary
        masked = self.apply_fov_boundary(masked, pan, tilt)

        ## Crop image to radius.
        srcw, srch = masked.shape[1], masked.shape[0]
        dstw = np.minimum(srcw, self.radius*2)
        dsth = np.minimum(srch, self.radius*2)

        x0, y0 = int((srcw-dstw)/2), int((srch-dsth)/2)
        x1, y1 = int(x0 + dstw), int(y0 +dsth)
        cropped = masked[y0:y1, x0:x1]
        
        return masked, cropped

    def get_threshold(self):
        self.mu.acquire()
        value = self.threshold
        self.mu.release()
        return value
    
    def set_threshold(self, value):
        self.mu.acquire()
        self.threshold = value
        self.mu.release()