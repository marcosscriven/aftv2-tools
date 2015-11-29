#!/usr/bin/env python3

import os
import time
import serial
import sys
import glob
import re

# read_mmc_win.py 1356644352 512 ver_4B4EC000.img
print ("executing: read_mmc_win.py 1356644352 512 ver_4B4EC000.img")
OSCALL = "read_mmc_win.py 1356644352 512 ver_4B4EC000.img"
#print (OSCALL)
os.system(OSCALL)
# find "5.0.3.1 (534011720)" ver_50DCC000.img
if '5.0.3.1 (534011720)' in open('ver_4B4EC000.img').read():
    print ('true')
# Version check success? IF else



# vim: ai et ts=4 sts=4 sw=4

