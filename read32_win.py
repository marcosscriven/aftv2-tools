#!/usr/bin/env python3

import sys, os
import serial
import struct

if os.path.exists("comport.txt"):
    fo = open("comport.txt", "r")
    PORT = fo.read()
    fo.close()
else:
    PORT       = "COM19"
    
BAUD = 115200

dev = serial.Serial(PORT, BAUD)

def print_hex_byte (data):

    print(len(data), end=": ")
    print(" ".join("0x{:02x}".format(x) for x in data))

def print_hex_word (data):

    print(len(data), end=": ")
    print(" ".join("0x{:08x}".format(x) for x in data))

def read32 (addr, size):

    result = []

    dev.write(b'\xd1')
    print_hex_byte(dev.read(1))

    dev.write(struct.pack('>I', addr))
    print_hex_byte(dev.read(4))

    dev.write(struct.pack('>I', size))
    print_hex_byte(dev.read(4))

    print_hex_byte(dev.read(2)) # status

    print("<===")
    for _ in range(size):
        data = dev.read(4)
        print_hex_byte(data)

        data = struct.unpack('>I', data)[0]
        result.append(data)
    print("<===")

    print_hex_byte(dev.read(2)) # status

    print()

    return result

if len(sys.argv) != 3:
    print("Usage: " + os.path.basename(sys.argv[0]) + " addr size")
    sys.exit(1)

addr = int(sys.argv[1], 0)
size = int(sys.argv[2], 0)

ret = read32(addr, size)

print_hex_word(ret)

# vim: ai et ts=4 sts=4 sw=4
