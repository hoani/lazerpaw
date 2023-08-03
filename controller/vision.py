import cv2 as cv
import numpy as np
from threading import Lock
import time

class ThresholdProcessor:
    def __init__(self):
        self.mu = Lock()
        self.threshold = 95
        self.radius = 25

    def process_frame(self, frame, pantilt):
        threshold = self.get_threshold()

        ## Note: It is slightly faster to resize, then threshold than the other way around.
        
        start = time.time()
        mono = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
        mono = cv.resize(mono, (80,60), cv.INTER_LINEAR)
        _, masked = cv.threshold(mono, threshold, 255, cv.THRESH_BINARY)

        ## Apply FOV boundary
        shape = masked.shape
        fov = 48.8
        ppdeg = shape[0]/fov
        xc, yc = shape[1]/2, shape[0]/2
        x, y = -pantilt.get_pan(), pantilt.get_tilt()
        xb, yb = pantilt.get_pan_boundary(), pantilt.get_tilt_boundary()
        x0, x1  = xc + (xb[0] - x)*ppdeg, xc + (xb[1] - x)*ppdeg
        y0, y1 = yc + (yb[0] - y)*ppdeg, yc + (yb[1] - y)*ppdeg
        mask = np.zeros(shape, dtype='uint8')
        cv.rectangle(mask, (int(x0), int(y0)), (int(x1), int(y1)), 255, thickness=cv.FILLED)
        cv.imshow("fov mask", mask)
        masked = cv.bitwise_and(masked, mask)
        cv.imshow("mask", masked)

        ## Crop image to radius.
        srcw, srch = masked.shape[1], masked.shape[0]
        dstw = np.minimum(srcw, self.radius*2)
        dsth = np.minimum(srch, self.radius*2)

        x0, y0 = int((srcw-dstw)/2), int((srch-dsth)/2)
        x1, y1 = int(x0 + dstw), int(y0 +dsth)
        cropped = masked[y0:y1, x0:x1]
        
        print("conversion time", time.time() - start)
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