#!/usr/bin/env python3

import os
import time
import serial

PORT = "/dev/ttyACM0"
BAUD = 115200

while True:

    if os.path.exists(PORT):
        break

    time.sleep(0.25)

dev = serial.Serial(PORT, BAUD)

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

print("Handshake Complete!")

# vim: ai et ts=4 sts=4 sw=4
