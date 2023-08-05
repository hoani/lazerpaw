import serial
import numpy as np
import time

class HSV:
    def __init__(self, h: int, s: int, v: int):
        self.h = h
        self.s = s
        self.v = v

    def str(self):
        return '{:02x}{:02x}{:02x}'.format(self.h, self.s, self.v)

class RGB:
    def __init__(self, r: int, g: int, b: int):
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

    def hsv(self, i, vals):
        result = 'I08\nH{:02x}'.format(i)
        for val in vals:
            result += val.str()
        result += '\n'
        self.ser.write(bytes(result, 'utf-8'))

    def rgb(self, i, vals):
        result = 'I08\nR{:02x}'.format(i)
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
        self.leds.hsv(0, self.idleVals)
        self.leds.show()

    def update_running(self, frac):
        hue = int(frac * 122)
        v = int(0x8f * (1 + np.sin(85*np.pi*frac)))
        runVal = HSV(hue, 0xff, v)
        vals = [runVal, runVal, runVal, runVal, runVal, runVal, runVal, runVal]
        self.leds.hsv(0, vals)
        self.leds.show()

    def update_manual(self):
        hue = int(180)
        v = int(0x8f * (1 + np.sin(0.5*np.pi*time.time())))
        runVal = HSV(hue, 0xff, v)
        vals = [runVal, runVal, runVal, runVal, runVal, runVal, runVal, runVal]
        self.leds.hsv(0, vals)
        self.leds.show()

    def update_shutdown(self, frac):
        hue = int(230)
        sat = int(0xff*(frac))
        vals = []
        count = int(np.ceil(frac * 8))
        for i in range(8):
            if i <= count:
                vals.append(HSV(hue, sat, 0xff))
            else:
                vals.append(HSV(hue, 0x00, 0x00))
        self.leds.hsv(0, vals)
        self.leds.show()



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

