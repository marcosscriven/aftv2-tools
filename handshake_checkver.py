#!/usr/bin/env python3

import os
import sys
import time
import serial
import glob

BAUD = 115200

def serial_ports ():
    """ Lists available serial ports

        :raises EnvironmentError:
            On unsupported or unknown platforms
        :returns:
            A set containing the serial ports available on the system
    """

    if sys.platform.startswith("win"):
        ports = [ "COM{0:d}".format(i + 1) for i in range(256) ]
    elif sys.platform.startswith("linux"):
        ports = glob.glob("/dev/ttyACM*")
    elif sys.platform.startswith("darwin"):
        ports = glob.glob("/dev/cu.usbmodem*")
    else:
        raise EnvironmentError("Unsupported platform")

    result = set()
    for port in ports:
        try:
            s = serial.Serial(port)
            s.close()
            result.add(port)
        except (OSError, serial.SerialException):
            pass

    return result

# serial checker
def check (test, gold):
    if test != gold:
        sys.stderr.write("ERROR: Serial protocol mismatch\n")
        sys.exit(1)

# write then read 1 byte
def write8 (out_str):
    dev.write(out_str)
    in_str = dev.read()
    return in_str

# initiate mtk preloader handshake
def handshake ():

    # look for start byte
    while True:
        c = write8(b'\xa0')
        if c == b'\x5f':
            break
        dev.flushInput()

    # complete sequence
    check(write8(b'\x0a'), b'\xf5')
    check(write8(b'\x50'), b'\xaf')
    check(write8(b'\x05'), b'\xfa')
    dev.close()

if __name__ == "__main__":

    port = None

    print("Waiting for preloader...")

    # detect preloader port
    old = serial_ports()
    while True:
        new = serial_ports()

        # port added
        if new > old:
            port = (new - old).pop()
            break
        # port removed
        elif old > new:
            old = new

        time.sleep(0.25)

    print("Found port = " + port)

    dev = serial.Serial(port, BAUD)
    handshake()

    print("Handshake complete!")

    # save port to file
    with open("comport.txt", 'w') as out:
        out.write(port)

    print ("Confirming AFTV2 OS Version is correct...")
    OSCALL = "read_mmc.py 0x50DCC000 512 ver_50DCC000.img"
    #print (OSCALL)
    os.system(OSCALL)
    # find version "5.0.3.1 (534011720)" in file ver_50DCC000.img
    if '5.0.3.1 (534011720)' in open('ver_50DCC000.img').read():
        print ("Version check passed: 5.0.3.1 (534011720)")
    else:
        print ("Version check failed: Not rootable with this method")
        os.remove("comport.txt")

# vim: ai et ts=4 sts=4 sw=4
