import numpy as np
import cv2 as cv

class Controller:
    MaxRate = 20 # deg/s
    def __init__(self, pantilt):
        self.pantilt = pantilt
        self.dx = 0
        self.dy = 0
        self.ddx = 0
        self.ddy = 0
        self.kf = 1.5 # Friction
        self.kr = 20 # Repulsion
        self.lazerCooldown = 10

        self.lazerOn = False
        self.d = []
        self.fx = []
        self.fy = []

        return

    def update(self, img: np.ndarray, dt: float):

        lazerSafe = True
        fx, fy = 0, 0
        
        shape = img.shape

        if len(self.d) == 0:
            self._init_control_matrices(shape)

        # Loop through each pixel.
        for i in range(shape[1]):
            for j in range(shape[0]):
                if img.data[j, i] == 0:
                    d = self.d[i][j]
                    if d < 2:
                        lazerSafe = False
                    
                    fx += self.fx[i][j]
                    fy += self.fy[i][j]
        
        ddx = self.kr * fx - self.dx * self.kf
        ddy = self.kr * fy - self.dy * self.kf
        dx = self.dx + dt * (self.ddx + ddx)/2 
        dy = self.dy + dt * (self.ddy + ddy)/2

        # Limit servo rates so we don't get too much integral windup.
        if np.abs(dx) > Controller.MaxRate:
            dx = np.sign(dx) * Controller.MaxRate
        if np.abs(dy) > Controller.MaxRate:
            dy = np.sign(dy) * Controller.MaxRate

        self.ddx = ddx
        self.ddy = ddy

        x = self.pantilt.get_pan() - dt * (self.dx + dx)/2 
        y = self.pantilt.get_tilt() - dt * (self.dy + dy)/2
        self.dx = dx
        self.dy = dy

        self.pantilt.pan(x)
        self.pantilt.tilt(y)

        if lazerSafe == False:
            self.lazerCooldown = 10
            self.lazerOn = False
        elif self.lazerOn == False:
            self.lazerCooldown -= 1
            if self.lazerCooldown == 0:
                self.lazerOn = True

    def yaw(self):
        return self.x
    
    def pitch(self):
        return self.y
    
    def lazer(self):
        return self.lazerOn
    

    def _init_control_matrices(self, shape):
        x0, y0 = shape[1]//2, shape[0]//2
        radius = x0
        if len(self.d) == 0:
            for i in range(shape[1]):
                x = (i-x0) 
                self.d.append([])
                self.fx.append([])
                self.fy.append([])
                for j in range(shape[0]):
                    y = (y0-j)
                    d = np.sqrt(x**2 + y**2)
                    fx = 0
                    fy = 0
                    ## centered elements and elements outside of the cropped radius have zero impact
                    if x != 0 and d < radius:
                        fx = -1/(x*d)
                    if y != 0 and d < radius:
                        fy = -1/(y*d)
                    self.d[i].append(d)
                    self.fx[i].append(fx)
                    self.fy[i].append(fy)




