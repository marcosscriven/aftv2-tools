#!/usr/bin/env python3

import os
import sys
import subprocess

# check version file
if not os.path.exists("version.txt"):
    sys.stderr.write(
        "ERROR: Missing version check file 'version.txt'\n")
    sys.exit(1)

# get version check values
with open("version.txt", 'r') as fin:
    fields = fin.read().split()
    buildprop_addr = int(fields[0], 0)
    buildprop_size = int(fields[1], 0)
    check_version = fields[2]

# extract build.prop file
print("Extracting build.prop...")
subprocess.check_call(
    [sys.executable,
        "read_mmc.py",
        hex(buildprop_addr),
        str(buildprop_size),
        "check_version.img"])

# analyze extracted data
with open("check_version.img", "r") as file_in:

    # look for fireos version
    for line in file_in:
        if line.startswith("ro.build.version.fireos="):

            # extract version
            version = line.rstrip().split("=")[1]

            # check if rootable
            if version == check_version:
                break
            else:
                print("NO, This device is not rootable (version = {0})".format(version))
                sys.exit(1)

    # we didn't find version
    else:
        sys.stderr.write(
            "ERROR: Extracted data does not contain build.prop\n")
        sys.exit(1)

print("YES, This device is rootable")

# vim: ai et ts=4 sts=4 sw=4
