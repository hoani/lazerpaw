import serial

ser = serial.Serial(
        port='/dev/serial0',
        baudrate = 115200,
        timeout=1
)

ser.write(b'I08\n')
ser.write(b'H0000ffff20ffff40ffff60ffff80ffffa0ffffc0ffffd0ffff\n')
ser.write(b'S\n')

