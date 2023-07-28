import serial
import numpy as np

class HSV:
    def __init__(self, h, s, v):
        self.h = h
        self.s = s
        self.v = v

    def str(self):
        return '{:02x}{:02x}{:02x}'.format(self.h, self.s, self.v)

class RGB:
    def __init__(self, r, g, b):
        self.r = r
        self.g = g
        self.b = b

    def str(self):
        return '{:02x}{:02x}{:02x}'.format(self.r, self.g, self.b)

class LEDs:
    def __init__(self):
        self.ser = serial.Serial(
            port='/dev/serial0',
            baudrate = 115200,
            timeout=1
        )
        self.ser.write(b'I08\n')

    def hsv(self, i, vals):
        result = 'H{:02x}'.format(i)
        for val in vals:
            result += val.str()
        result += '\n'
        self.ser.write(bytes(result, 'utf-8'))

    def rgb(self, i, vals):
        result = 'R{:02x}'.format(i)
        for val in vals:
            result += val.rgb()
        result += '\n'
        self.ser.write(bytes(result, 'utf-8'))

    def show(self):
        self.ser.write(b'S\n')

class Status:
    def __init__(self):
        self.leds = LEDs()
        self.idleVals = [
            HSV(0x00,0xff,0xff), HSV(0x20,0xff,0xff), HSV(0x40,0xff,0xff), HSV(0x60,0xff,0xff),
            HSV(0x80,0xff,0xff), HSV(0xa0,0xff,0xff), HSV(0xb0,0xff,0xff), HSV(0xc0,0xff,0xff),
        ]

    def update_idle(self):
        for val in self.idleVals:
            val.h=(val.h + 1) % 0xff
        leds.hsv(0, vals)
        leds.show()

    def update_running(self, frac):
        hue = int((1-frac) * 122)
        v = np.sin(85*np.pi*frac)
        runVal = HSV(hue, 255, v)
        vals = [runVal, runVal, runVal, runVal, runVal, runVal, runVal, runVal]
        leds.hsv(0, vals)
        leds.show()

    def update_manual(self):
        hue = int(180)
        vals = []
        for i in range(8):
            val = int(i * 32 + time.time()*8) % 256
            vals.append(HSV(hue, 255, val))
        leds.hsv(0, vals)
        leds.show()

    def update_shutdown(self, frac):
        hue = int(220)
        sat = 255*(1-frac)
        vals = []
        for i in range(8):
            val = int(i * 32 + frac * 2560) % 256
            vals.append(HSV(hue, sat, val))
        leds.hsv(0, vals)
        leds.show()



if __name__ == "__main__":

    import time 

    leds=LEDs()
    vals = [
        HSV(0x00,0xff,0xff), HSV(0x20,0xff,0xff), HSV(0x40,0xff,0xff), HSV(0x60,0xff,0xff),
        HSV(0x80,0xff,0xff), HSV(0xa0,0xff,0xff), HSV(0xb0,0xff,0xff), HSV(0xc0,0xff,0xff),
        ]
    while True:
        leds.hsv(0, vals)
        leds.show()
        for val in vals:
            val.h=(val.h + 1) % 0xff
        time.sleep(1/64)
# ser.write(b'I08\n')
# ser.write(b'H0000ffff20ffff40ffff60ffff80ffffa0ffffc0ffffd0ffff\n')
# ser.write(b'S\n')

