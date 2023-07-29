import numpy as np

class Controller:
    def __init__(self, pan0, tilt0, panBounds, tiltBounds):
        self.x = pan0
        self.y = tilt0
        self.dx = 0
        self.dy = 0
        self.ddx = 0
        self.ddy = 0
        self.kf = 0.2 # Friction
        self.kr = 10 # Repulsion
        self.lazerCooldown = 10

        self.xmin = panBounds[0]
        self.xmax = panBounds[1]

        self.ymin = tiltBounds[0]
        self.ymax = tiltBounds[1]

        self.lazerOn = False
        self.d = []
        self.fx = []
        self.fy = []

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
        x0, y0 = shape[1]//2, shape[0]//2

        if len(self.d) == 0:
            self._init_control_matrices(shape)

        # This is the cause of the lower frame rate
        for i in range(shape[1]):
            x = -(i-x0) # Note: the camera orientation makes this inverted
            for j in range(shape[0]):
                y = -(y0-j) # Note: the camera orientation makes this inverted

                if img.data[j, i] == 0:
                    d = self.d[i][j]
                    if d < 2:
                        lazerSafe = False
                    else:
                        if d < x0:
                            if x != 0:
                                fx += self.fx[i][j]
                            if y != 0:
                                fy += self.fy[i][j]
        
        ddx = self.kr * fx - self.dx * self.kf
        ddy = self.kr * fy - self.dy * self.kf
        dx = self.dx + dt * (self.ddx + ddx)/2 
        dy = self.dy + dt * (self.ddy + ddy)/2 
        self.ddx = ddx
        self.ddy = ddy

        self.x = self.x - dt * (self.dx + dx)/2 
        self.y = self.y - dt * (self.dy + dy)/2
        self.dx = dx
        self.dy = dy

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
    

    def _init_control_matrices(self, shape):
        x0, y0 = shape[1]//2, shape[0]//2
        if len(self.d) == 0:
            for i in range(shape[1]):
                x = -(i-x0)
                self.d.append([])
                self.fx.append([])
                self.fy.append([])
                for j in range(shape[0]):
                    y = -(y0-j)
                    d = np.sqrt(x**2 + y**2)
                    fx = -1/(x*d)
                    fy = -1/(y*d)
                    self.d[i].append(d)
                    self.fx[i].append(fx)
                    self.fy[i].append(fy)




