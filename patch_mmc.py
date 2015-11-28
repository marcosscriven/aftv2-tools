#!/usr/bin/env python3

import os
import time
import serial
import sys
import glob
import re

# Patch MMC logic
filelist = (sorted(glob.glob('patch_*.img')))
print (filelist)
print (filelist[0])

for file in filelist:
    print ("current file: ", file)
    #fo = open(file, "r")
    #contents = fo.read()
    #fo.close()
    #print (file, " contents:")
    #print (contents)
    # tokenize filename splitting on _ and . to find pysh addr 2nd last token
    tokens = re.split("[_.]", file)
    #print ("tokens:", tokens)
    ADDR = tokens[-2]
    print ("ADDR:", ADDR)
    print ("executing: write_mmc_win.py ", ADDR, " " ,file)
    OSCALL = "write_mmc_win.py " + ADDR + " " + file
    print (OSCALL)
    os.system(OSCALL)



# vim: ai et ts=4 sts=4 sw=4

