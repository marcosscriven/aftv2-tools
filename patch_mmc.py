#!/usr/bin/env python3

import sys
import re
import glob
import subprocess

# patch file patterns
patch_list = sorted(glob.glob("patch_*.img"))
patch_regex = re.compile(r'patch_([0-9a-f]+)\.img')

for patch in patch_list:

    print("Patching {0}...".format(patch))

    # extract address
    match = patch_regex.match(patch)
    if not match:
        sys.stderr.write(
            "ERROR: '{0}' does not match expected pattern\n".format(patch))
        sys.exit(1)

    phys_addr = int(match.group(1), 16)

    # apply patch file
    subprocess.check_call([
        sys.executable, "write_mmc.py", hex(phys_addr), patch])

# vim: ai et ts=4 sts=4 sw=4
