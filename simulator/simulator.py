import cv2 as cv
import numpy as np


class Cat():
    def __init__(self, x, y):
        img = cv.imread("cat2.png", cv.IMREAD_UNCHANGED)
        self.img = cv.resize(img, (240,240), interpolation=cv.INTER_NEAREST)
        self.x = x
        self.y = y

    def draw(self, img):
        (w, h) = (self.img.shape[1], self.img.shape[0])
        (ymin, ymax, xmin, xmax) = (self.y,self.y+h, self.x,self.x+w)
        sub_img = img[ymin:ymax, xmin:xmax]
        b,g,r,mask = cv.split(self.img)
        _, mask = cv.threshold(mask, 100, 255, cv.THRESH_BINARY_INV)
        sub_img = cv.bitwise_and(sub_img, sub_img, mask=mask)

        res = cv.addWeighted(cv.merge([b,g,r]), 1, sub_img, 1, 0)

        # Putting the image back to its position
        img[ymin:ymax, xmin:xmax] = res

class Room():
    def __init__(self, roomSize=(3200,2400)):
        self.size=roomSize

class Camera():
    vfov = 48.8 * (np.pi/180)
    hfov = 62.2 * (np.pi/180)
    imageSize=(640,480)

    def __init__(self, height=1200, room=Room()):
        self.theta = 45 * (np.pi / 180) # 0 deg = pointing down
        self.phi = 0 # 0 deg = pointing forward
        self.height=height
        self.room=room

    def incrementPan(self, delta):
        phi = self.phi + delta

        if phi < -np.pi / 8:
            phi = -np.pi / 8
        if phi > np.pi /8:
            phi = np.pi / 8

        self.phi = phi

    def incrementTilt(self, delta):
        theta = self.theta + delta

        if theta < np.pi / 8:
            theta = np.pi / 8
        if theta > 4*np.pi /8:
            theta = 4*np.pi /8

        self.theta = theta

    # The math isn't quite right here... but for an approximation it's ok.
    def floorIntersection(self, xangle, yangle):
        dy = np.tan(yangle) * self.height
        dx = np.tan(xangle) * self.height
        
        x = self.room.size[0]/2 + np.sin(xangle) * dy  + np.cos(yangle) * dx
        y = self.room.size[1] - np.cos(xangle) * dy + np.sin(xangle) * dx
        return [x, y]
    
    def projection(self):
        thetaMin = self.theta - __class__.vfov/2
        thetaMax = self.theta + __class__.vfov/2
        phiMin = self.phi - __class__.hfov/2
        phiMax = self.phi + __class__.hfov/2

        pts = np.float32([
            self.floorIntersection(phiMin, thetaMax), self.floorIntersection(phiMax, thetaMax), 
            self.floorIntersection(phiMin, thetaMin), self.floorIntersection(phiMax, thetaMin),
        ])

        lens = np.float32([
            [0, 0], [__class__.imageSize[0], 0],
            [0, __class__.imageSize[1]], [__class__.imageSize[0], __class__.imageSize[1]]
        ])
        # Apply Perspective Transform Algorithm
        return cv.getPerspectiveTransform(pts, lens)
    
    def takeFrame(self, image, projection):
        return cv.warpPerspective(image, projection, __class__.imageSize)
        
    




class Simulation():
    def __init__(self, room=Room(), camera=Camera(), floorSrc="floor1.jpg"):
        self.room=room
        self.camera=camera

        self.blankRoom = cv.cvtColor(
            np.zeros((self.room.size[1], self.room.size[0]), dtype='uint8'), 
            cv.COLOR_GRAY2BGR
            )

        self.floortexture = cv.resize(
            np.tile(cv.imread(floorSrc), (3, 3, 1)), 
            self.room.size,
        )
        self.floor = self.floortexture
        self.cat = Cat(200,200)
        self.cat.draw(self.floor)

    def update(self):
        print('theta: {:.1f}, phi: {:.1f}'.format(180*self.camera.theta/np.pi, 180*self.camera.phi/np.pi))

        matrix = self.camera.projection()
        result = self.camera.takeFrame(self.floor, matrix)
        
        cv.imshow('Transformed', result)

        ones = np.ones((Camera.imageSize[1], Camera.imageSize[0]), dtype='uint8')
        light = cv.merge([0*ones,255*ones,255*ones])
        cameraArea = cv.warpPerspective(light, np.linalg.inv(matrix), room.size)

        floorOverlay = cv.addWeighted(self.floor.copy(), 0.8, cameraArea, 0.2, 1)
        
        cv.imshow('Floor', cv.resize(floorOverlay, Camera.imageSize))


room = Room()
camera = Camera()
sim = Simulation(room=room, camera=camera)

while True:
    
    sim.update()

    pressed = cv.waitKey(0)

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


