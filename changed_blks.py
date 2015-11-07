#!/usr/bin/env python3

import os
import sys

BLOCK_SIZE = 512 # bytes

# check usage
if len(sys.argv) != 2:
    print("Usage: " + os.path.basename(sys.argv[0]) + " diff_file")
    sys.exit(1)

used_blocks = set()

# read each line
with open(sys.argv[1], 'r') as input:
    for line in input:

        # save unique block addr
        offset = int(line.split()[0])
        block = int(offset / BLOCK_SIZE)
        used_blocks.add(block)

used_blocks = sorted(used_blocks)

start_block = used_blocks[0]
block_length = 1

# find contiguous blocks
for index in range(1, len(used_blocks)):

    block = used_blocks[index]
    last_block = used_blocks[index - 1]

    # block continues
    if block == (last_block + 1):
        block_length += 1

    # new block
    else:

        # print previous region
        print("0x{0:x} {1:d}".format(
            start_block * BLOCK_SIZE, block_length * BLOCK_SIZE))

        start_block = block
        block_length = 1

# print final region
print("0x{0:x} {1:d}".format(
    start_block * BLOCK_SIZE, block_length * BLOCK_SIZE))

# vim: ai et ts=4 sts=4 sw=4
