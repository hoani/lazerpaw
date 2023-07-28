import serial

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

