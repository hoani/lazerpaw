import cv2 as cv
import numpy as np

class Camera():
    vfov = 48.8 * (np.pi/180)
    hfov = 62.2 * (np.pi/180)
    imageSize=(640,480)

    def __init__(self):
        cap = cv.VideoCapture(0)
        cap.set(cv.CAP_PROP_FRAME_WIDTH, Camera.imageSize[0])
        cap.set(cv.CAP_PROP_FRAME_HEIGHT, Camera.imageSize[1])
        self.cap = cap
    
    def frame(self):
        while True:
            isTrue, frame = self.cap.read()
            frame = cv.flip(frame, -1)
            if not isTrue:
                break
            yield(frame)

    def release(self):
        self.cap.release()