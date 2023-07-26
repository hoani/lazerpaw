import cv2 as cv
from threading import Lock

class ThresholdProcessor:
    def __init__(self):
        self.mu = Lock()
        self.threshold = 95

    def process_frame(self, frame):
        threshold = self.get_threshold()

        gray = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
        _, masked = cv.threshold(gray, threshold, 255, cv.THRESH_BINARY)
        masked = cv.resize(masked, (40,30))
        
        return masked

    def get_threshold(self):
        self.mu.acquire()
        value = self.threshold
        self.mu.release()
        return value
    
    def set_threshold(self, value):
        self.mu.acquire()
        self.threshold = value
        self.mu.release()