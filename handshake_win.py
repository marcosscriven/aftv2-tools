#!/usr/bin/env python3

import os
import time
import serial
import sys
import glob


#PORT = "COM20"
BAUD = 115200

def serial_ports():
    """ Lists serial port names

        :raises EnvironmentError:
            On unsupported or unknown platforms
        :returns:
            A list of the serial ports available on the system
    """
    if sys.platform.startswith('win'):
        ports = ['COM%s' % (i + 1) for i in range(256)]
    elif sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
        # this excludes your current terminal "/dev/tty"
        ports = glob.glob('/dev/tty[A-Za-z]*')
    elif sys.platform.startswith('darwin'):
        ports = glob.glob('/dev/tty.*')
    else:
        raise EnvironmentError('Unsupported platform')

    result = []
    for port in ports:
        try:
            s = serial.Serial(port)
            s.close()
            result.append(port)
        except (OSError, serial.SerialException):
            pass
    return result


if __name__ == '__main__':
    output = serial_ports()
    newport = []
    while True:
        output_new = serial_ports()
        print(output_new)
        if output != output_new:
            newport = list(set(output_new) - set(output))
            break
        time.sleep(0.25)

print (newport[0])
dev = serial.Serial(newport[0], BAUD)




def print_hex (data):

    print(len(data), end=": ")
    print(" ".join(hex(x) for x in data))

def write8 (out_str):

    print_hex(out_str)
    dev.write(out_str)
    in_str = dev.read()
    print_hex(in_str)

    return in_str

while True:

    c = write8(b'\xa0')
    if c == b'\x5f':
        break
    dev.flushInput()

write8(b'\x0a')
write8(b'\x50')
write8(b'\x05')

print("Handshake Complete! used port:", newport[0])
fo = open("comport.txt", "w")
fo.write(newport[0])
fo.close()

# vim: ai et ts=4 sts=4 sw=4
