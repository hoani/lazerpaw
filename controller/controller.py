import numpy as np

class Controller:
    def __init__(self, x0, y0, xbounds, ybounds):
        self.x = x0
        self.y = y0
        self.dx = 0
        self.dy = 0
        self.ddx = 0
        self.ddy = 0
        self.kf = 1.5 # Friction
        self.kr = 10 # Repulsion
        self.radius = 60
        self.lazerCooldown = 10

        self.xmin = xbounds[0]
        self.xmax = xbounds[1]

        self.ymin = ybounds[0]
        self.ymax = ybounds[1]

        self.lazerOn = False

        return

    def apply_bounds(self):
        if self.x < self.xmin:
            self.x = self.xmin
        if self.x > self.xmax:
            self.x = self.xmax
        if self.y < self.ymin:
            self.y = self.ymin
        if self.y > self.ymax:
            self.y = self.ymax

    def update(self, img: np.ndarray, dt: float):

        lazerSafe = True
        fx, fy = 0, 0
        shape = img.shape
        x0, y0 = img.shape[1]//2, img.shape[0]//2
        for i in range(shape[1]):
            x = i-x0
            for j in range(shape[0]):
                y = y0-j

                if img.data[j, i] == 0:
                    if x == 0 and y == 0:
                        lazerSafe = False
                    else:
                        d2 = x**2 + y**2
                        if d2 < self.radius**2:
                            fx += -x/d2
                            fy += -y/d2
        
        ddx = self.kr * fx - self.dx * 0.2
        ddy = self.kr * fy - self.dx * 0.2
        dx = self.dx + dt * (self.ddx + ddx)/2 
        dy = self.dy + dt * (self.ddy + ddy)/2 
        self.ddx = ddx
        self.ddy = ddy

        # dx = self.kr * fx 
        # dy = self.kr * fy

        self.x = self.x - dt * (self.dx + dx)/2 
        self.y = self.y - dt * (self.dy + dy)/2

        self.apply_bounds()

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




