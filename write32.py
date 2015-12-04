#!/usr/bin/env python3

import sys, os
import serial
import struct

BAUD = 115200

# check port file
if not os.path.exists("comport.txt"):
    sys.stderr.write(
        "ERROR: Missing 'comport.txt', run handshake.py first\n")
    sys.exit(1)

# get handshaked port
with open("comport.txt", 'r') as fin:
    port = fin.read()

# open port
dev = serial.Serial(port, BAUD)

def print_hex_byte (data):

    print(len(data), end=": ")
    print(" ".join("0x{:02x}".format(x) for x in data))

def print_hex_word (data):

    print(len(data), end=": ")
    print(" ".join("0x{:08x}".format(x) for x in data))

def write32 (addr, words):

    dev.write(b'\xd4')
    print_hex_byte(dev.read(1))

    dev.write(struct.pack('>I', addr))
    print_hex_byte(dev.read(4))

    dev.write(struct.pack('>I', len(words)))
    print_hex_byte(dev.read(4))

    print_hex_byte(dev.read(2)) # status

    print("===>")
    for word in words:
        dev.write(struct.pack('>I', word))
        print_hex_byte(dev.read(4))
    print("===>")

    print_hex_byte(dev.read(2)) # status

    print()

if len(sys.argv) < 3:
    print("Usage: " + os.path.basename(sys.argv[0]) + " addr words...")
    sys.exit(1)

addr = int(sys.argv[1], 0)
words = [int(x, 0) for x in sys.argv[2:]]

write32(addr, words)

# vim: ai et ts=4 sts=4 sw=4
