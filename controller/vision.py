import cv2 as cv
import numpy as np
from threading import Lock

class ThresholdProcessor:
    def __init__(self):
        self.mu = Lock()
        self.threshold = 95
        self.radius = 25

    def process_frame(self, frame):
        threshold = self.get_threshold()

        ## Note: It is slightly faster to resize, then threshold than the other way around.
        gray = cv.resize(cv.cvtColor(frame, cv.COLOR_BGR2GRAY), (80,60), cv.INTER_LINEAR)
        _, masked = cv.threshold(gray, threshold, 255, cv.THRESH_BINARY)

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