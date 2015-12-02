#!/usr/bin/env python3

import sys
import subprocess

BUILDPROP_ADDR = 0x50dcc000  # phys addr
BUILDPROP_SIZE = 4096 * 2    # 2 blocks

# extract build.prop file
print("Extracting build.prop...")
subprocess.check_call(
    ["./read_mmc.py",
        hex(BUILDPROP_ADDR),
        str(BUILDPROP_SIZE),
        "check_version.img"])

# analyze extracted data
with open("check_version.img", "r") as file_in:

    # look for fireos version
    for line in file_in:
        if line.startswith("ro.build.version.fireos="):

            # extract version
            version = line.rstrip().split("=")[1]

            # check if rootable
            if version == "5.0.3.1":
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
