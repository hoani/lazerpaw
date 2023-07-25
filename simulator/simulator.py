import cv2 as cv
import numpy as np
import os

basePath = os.path.basename(os.path.dirname(__file__)) + "/"

def src(filename):
    return basePath + filename

class Cat():
    def __init__(self, x, y):
        img = cv.imread(src("cat1.png"), cv.IMREAD_UNCHANGED)
        self.img = cv.resize(img, (400,600), interpolation=cv.INTER_NEAREST)
        self.x = x
        self.y = y
        self.spd = 10

    def update(self, lazerPos):
        if lazerPos[0] < self.x:
            vx = -1*self.spd
        else:
            vx = 1*self.spd

        if lazerPos[1] < self.y:
            vy = -1*self.spd
        else:
            vy = 1*self.spd

        self.x += vx
        self.y += vy

    def draw(self, img):
        (w_2, h_2) = (self.img.shape[1]//2, self.img.shape[0]//2)
        (xoffset, yoffset) = (self.x-w_2, self.y-h_2)
        (ymin, ymax, xmin, xmax) = (yoffset, yoffset + 2*h_2, xoffset, xoffset + 2*w_2)
        if xmax < 0 or ymax < 0 or xmin >= img.shape[1] or ymin >= img.shape[0]:
            return # Nothing to draw
        if ymin < 0:
            ymin = 0
        if ymax >= img.shape[0]:
            ymax = img.shape[0]-1
        if xmin < 0:
            xmin = 0
        if xmax >= img.shape[1]:
            xmax = img.shape[1]-1
        sub_img = img[ymin:ymax, xmin:xmax]
        b,g,r,mask = cv.split(self.img.copy()[ymin-yoffset:ymax-yoffset, xmin-xoffset:xmax-xoffset])
        _, mask = cv.threshold(mask, 100, 255, cv.THRESH_BINARY_INV)        
        sub_img = cv.bitwise_and(sub_img, sub_img, mask=mask)

        res = cv.addWeighted(cv.merge([b,g,r]), 1, sub_img, 1, 0)

        # Putting the image back to its position
        img[ymin:ymax, xmin:xmax] = res

class Room():
    def __init__(self, roomSize=(3000,3000)):
        self.size=roomSize

class Camera():
    vfov = 48.8 * (np.pi/180)
    hfov = 62.2 * (np.pi/180)
    imageSize=(640,480)

    def __init__(self, height=1800, room=Room()):
        self.theta = 45 * (np.pi / 180) # 0 deg = pointing down
        self.phi = 0 # 0 deg = pointing forward
        self.height=height
        self.room=room
        self.tiltMin = np.pi/32
        self.tiltMax = np.arctan2(3,2)

    def commandPan(self, phi):
        if phi < -np.pi / 8:
            phi = -np.pi / 8
        if phi > np.pi /8:
            phi = np.pi / 8

        self.phi = phi

    def commandTilt(self, theta):
        if theta < self.tiltMin:
            theta = self.tiltMin
        if theta > self.tiltMax:
            theta = self.tiltMax

        self.theta = theta

    def incrementPan(self, delta):
        self.commandPan(self.phi + delta)

    def incrementTilt(self, delta):
        self.commandTilt(self.theta + delta)


    def center(self):
        return self.floorIntersection(self.phi, self.theta)

    # The math isn't quite right here... but for an approximation it's ok.
    def floorIntersection(self, xangle, yangle):
        dy = np.tan(yangle) * self.height
        dx = np.tan(xangle) * self.height
        
        x = self.room.size[0]/2 + np.sin(xangle) * dy  + np.cos(yangle) * dx
        y = self.room.size[1] - np.cos(xangle) * dy + np.sin(xangle) * dx
        return (x, y)
    
    def projection(self):
        thetaMin = self.theta - __class__.vfov/2
        thetaMax = self.theta + __class__.vfov/2
        phiMin = self.phi - __class__.hfov/2
        phiMax = self.phi + __class__.hfov/2

        pts = np.float32([
            self.floorIntersection(phiMin, thetaMin),  
            self.floorIntersection(phiMin, thetaMax),  
            self.floorIntersection(phiMax, thetaMax),  
            self.floorIntersection(phiMax, thetaMin), 
        ])

        xMin, xMax = 0,  __class__.imageSize[0]
        yMin, yMax = 0,  __class__.imageSize[1]
        lens = np.float32([
            [xMin, yMax], 
            [xMin, yMin], 
            [xMax, yMin],
            [xMax, yMax], 
        ])

        # Apply Perspective Transform Algorithm
        return cv.getPerspectiveTransform(pts, lens)
    
    def takeFrame(self, image, projection):
        return cv.warpPerspective(image, projection, __class__.imageSize)
        
    




class Simulation():
    def __init__(self, room=Room(), camera=Camera(), floorSrc=src("floor1.jpg")):
        self.room=room
        self.camera=camera
        self.lazerOn = False

        self.blankRoom = cv.cvtColor(
            np.zeros((self.room.size[1], self.room.size[0]), dtype='uint8'), 
            cv.COLOR_GRAY2BGR
            )

        self.floortexture = cv.resize(
            np.tile(cv.imread(floorSrc), (3, 3, 1)), 
            self.room.size,
        )
        self.floor = self.floortexture.copy()
        self.cats = []

    def addCat(self, cat: Cat):
        self.cats.append(cat)

    def update(self):
        matrix = self.camera.projection()
        invMatrix = np.linalg.inv(matrix)
        self.floor = self.floortexture.copy()

        if self.lazerOn:
            # Compute lazer position using matrix equation in https://docs.opencv.org/4.x/da/d54/group__imgproc__transform.html.
            lx, ly = Camera.imageSize[0]//2, Camera.imageSize[1]//2
            lazerx = (invMatrix[0,0] * lx + invMatrix[0,1] * ly + invMatrix[0,2]) / (invMatrix[2,0] * lx + invMatrix[2,1] * ly + invMatrix[2,2])
            lazery = (invMatrix[1,0] * lx + invMatrix[1,1] * ly + invMatrix[1,2]) / (invMatrix[2,0] * lx + invMatrix[2,1] * ly + invMatrix[2,2])

            lazerPos = (lazerx, lazery)

            for c in self.cats:
                c.update(lazerPos)
            cv.circle(self.floor, (int(lazerPos[0]), int(lazerPos[1])), 10, (120, 120, 255), thickness=cv.FILLED)

        for c in self.cats:
            c.draw(self.floor)


        print('theta: {:.1f}, phi: {:.1f}'.format(180*self.camera.theta/np.pi, 180*self.camera.phi/np.pi))

        result = self.camera.takeFrame(self.floor, matrix)
        
        ones = np.ones((Camera.imageSize[1], Camera.imageSize[0]), dtype='uint8')
        light = cv.merge([0*ones,255*ones,255*ones])
        cameraArea = cv.warpPerspective(light, invMatrix, self.room.size)

        floorOverlay = cv.addWeighted(self.floor.copy(), 0.8, cameraArea, 0.2, 1)
        
        cv.imshow('Floor', cv.resize(floorOverlay, Camera.imageSize))

        return result


# Manual Control
if __name__ == "__main__":
    room = Room()
    camera = Camera()
    sim = Simulation(room=room, camera=camera)
    sim.addCat(Cat(400,400))

    while True:
        
        sim.update()

        pressed = cv.waitKey(10)

        if pressed == -1:
            continue

        UP = 0
        DOWN = 1
        LEFT = 2
        RIGHT = 3


        if pressed is UP:
            camera.incrementTilt(1* (np.pi / 180))
        elif pressed is DOWN:
            camera.incrementTilt(-1* (np.pi / 180))
        elif pressed is LEFT:
            camera.incrementPan(-1* (np.pi / 180))
        elif pressed is RIGHT:
            camera.incrementPan(1* (np.pi / 180))
        else:
            exit(0)


