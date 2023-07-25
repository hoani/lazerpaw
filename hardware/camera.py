import numpy as np
from servo import PanTilt

class Camera():
    vfov = 48.8 * (np.pi/180)
    hfov = 62.2 * (np.pi/180)
    imageSize=(640,480)

    def __init__(self, capture):
        self.capture = capture      



    
    def takeFrame(self, image, projection):
        return cv.warpPerspective(image, projection, __class__.imageSize)