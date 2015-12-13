#!/usr/bin/env python3

import os
import sys
import time
import re
import glob
import struct
import serial

BAUD = 115200
BASE_ADDR = 0x11230000    # mtk-msdc.0
BLOCK_SIZE = 512          # bytes
SYSTEM_ADDR = 0x058e0000  # part addr


# common definition
MSDC_FIFO_SZ          = 128
MSDC_FIFO_THD         = 64

# common register
MSDC_INT              = BASE_ADDR + 0x0c
MSDC_FIFOCS           = BASE_ADDR + 0x14
MSDC_TXDATA           = BASE_ADDR + 0x18
MSDC_RXDATA           = BASE_ADDR + 0x1c

# sdmmc register
MSDC_CMD              = BASE_ADDR + 0x34
MSDC_ARG              = BASE_ADDR + 0x38
MSDC_STS              = BASE_ADDR + 0x3c
MSDC_RESP0            = BASE_ADDR + 0x40

# MSDC_INT mask
MSDC_INT_CMDRDY       = 0x1 << 8
MSDC_INT_CMDTMO       = 0x1 << 9
MSDC_INT_RSPCRCERR    = 0x1 << 10
MSDC_INT_XFER_COMPL   = 0x1 << 12
MSDC_INT_DATTMO       = 0x1 << 14
MSDC_INT_DATCRCERR    = 0x1 << 15

# MSDC_FIFOCS mask
MSDC_FIFOCS_RXCNT     = 0xff << 0
MSDC_FIFOCS_TXCNT     = 0xff << 16

# MSDC_STS mask
MSDC_STS_SDCBUSY      = 0x1 << 0

# mmc command
MMC_READ_SINGLE_BLOCK = 17
MMC_WRITE_BLOCK       = 24

# command response
MSDC_RESP_R1          = 1

# mmc status R1
MMC_R1_OUT_OF_RANGE   = 0x1 << 31


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

# serial checkers
def check (test, gold):
    if test != gold:
        sys.stderr.write("ERROR: Serial protocol mismatch\n")
        sys.exit(1)
def check_int (test, gold):
    test = struct.unpack('>I', test)[0]
    check(test, gold)

# write then read 1 byte
def write8 (out_str):
    dev.write(out_str)
    in_str = dev.read()
    return in_str

# read 32-bit array from address
def sdr_read32 (addr, size=1):

    result = []

    dev.write(b'\xd1')
    check(dev.read(1), b'\xd1') # echo cmd

    dev.write(struct.pack('>I', addr))
    check_int(dev.read(4), addr) # echo addr

    dev.write(struct.pack('>I', size))
    check_int(dev.read(4), size) # echo size

    check(dev.read(2), b'\x00\x00') # arg check

    for _ in range(size):
        data = struct.unpack('>I', dev.read(4))[0]
        result.append(data)

    check(dev.read(2), b'\x00\x00') # status

    # support scalar
    if len(result) == 1:
        return result[0]
    else:
        return result

# write 32-bit array to address
def sdr_write32 (addr, words):

    # support scalar
    if not isinstance(words, list):
        words = [ words ]

    dev.write(b'\xd4')
    check(dev.read(1), b'\xd4') # echo cmd

    dev.write(struct.pack('>I', addr))
    check_int(dev.read(4), addr) # echo addr

    dev.write(struct.pack('>I', len(words)))
    check_int(dev.read(4), len(words)) # echo size

    check(dev.read(2), b'\x00\x00') # arg check

    for word in words:
        dev.write(struct.pack('>I', word))
        check_int(dev.read(4), word) # echo word

    check(dev.read(2), b'\x00\x00') # status

# fifo helpers
def msdc_txfifocnt ():
    return (sdr_read32(MSDC_FIFOCS) & MSDC_FIFOCS_TXCNT) >> 16
def msdc_rxfifocnt ():
    return (sdr_read32(MSDC_FIFOCS) & MSDC_FIFOCS_RXCNT) >> 0
def msdc_fifo_write32 (word):
    sdr_write32(MSDC_TXDATA, word)
def msdc_fifo_read32 ():
    return sdr_read32(MSDC_RXDATA)

# cmd :
# vol_swt << 30 | auto_cmd << 28 | blklen << 16 | go_irq << 15 |
# stop << 14 | rw << 13 | dtype << 11 | rsptyp << 7 | brk << 6 | opcode

# command helpers
def sdc_send_cmd (cmd, arg):
    sdr_write32(MSDC_ARG, arg)
    sdr_write32(MSDC_CMD, cmd)
def sdc_is_busy ():
    return True if sdr_read32(MSDC_STS) & MSDC_STS_SDCBUSY else False

# read data from fifo in pio mode
def msdc_pio_read (size):

    result = []

    left = size
    get_xfer_done = False
    wints = MSDC_INT_DATTMO | MSDC_INT_DATCRCERR | MSDC_INT_XFER_COMPL
    ints = 0

    while True:

        # ack interrupts
        if not get_xfer_done:
            ints = sdr_read32(MSDC_INT)
            ints &= wints
            sdr_write32(MSDC_INT, ints)

        # check interrupts
        if ints & MSDC_INT_DATTMO:
            sys.stderr.write("ERROR: Data Timeout\n")
            sys.exit(1)
        elif ints & MSDC_INT_DATCRCERR:
            sys.stderr.write("ERROR: Data CRC Error\n")
            sys.exit(1)
        elif ints & MSDC_INT_XFER_COMPL:
            get_xfer_done = True
            if left == 0:
                break

        while left > 0:

            # more than threshold
            if (left >= MSDC_FIFO_THD) and (msdc_rxfifocnt() >= MSDC_FIFO_THD):

                for _ in range(MSDC_FIFO_THD >> 2):
                    result.append(msdc_fifo_read32())
                left -= MSDC_FIFO_THD

            # less than threshold
            elif (left < MSDC_FIFO_THD) and (msdc_rxfifocnt() >= left):

                while left > 0:
                    result.append(msdc_fifo_read32())
                    left -= 4

            else:

                ints = sdr_read32(MSDC_INT)

                # check interrupts
                if ints & MSDC_INT_DATTMO:
                    sys.stderr.write("ERROR: Data Timeout\n")
                    sdr_write32(MSDC_INT, ints)
                    sys.exit(1)
                elif ints & MSDC_INT_DATCRCERR:
                    sys.stderr.write("ERROR: Data CRC Error\n")
                    sdr_write32(MSDC_INT, ints)
                    sys.exit(1)

    return result

# write data to fifo in pio mode
def msdc_pio_write (words):

    left = len(words) * 4
    get_xfer_done = False
    wints = MSDC_INT_DATTMO | MSDC_INT_DATCRCERR | MSDC_INT_XFER_COMPL
    ints = 0

    while True:

        # ack interrupts
        if not get_xfer_done:
            ints = sdr_read32(MSDC_INT)
            ints &= wints
            sdr_write32(MSDC_INT, ints)

        # check interrupts
        if ints & MSDC_INT_DATTMO:
            sys.stderr.write("ERROR: Data Timeout\n")
            sys.exit(1)
        elif ints & MSDC_INT_DATCRCERR:
            sys.stderr.write("ERROR: Data CRC Error\n")
            sys.exit(1)
        elif ints & MSDC_INT_XFER_COMPL:
            get_xfer_done = True
            if left == 0:
                break

        while left > 0:

            # more than fifo size
            if (left >= MSDC_FIFO_SZ) and (msdc_txfifocnt() == 0):

                for _ in range(MSDC_FIFO_SZ >> 2):
                    msdc_fifo_write32(words.pop(0))
                left -= MSDC_FIFO_SZ

            # less than fifo size
            elif (left < MSDC_FIFO_SZ) and (msdc_txfifocnt() == 0):

                while left > 0:
                    msdc_fifo_write32(words.pop(0))
                    left -= 4

            else:

                ints = sdr_read32(MSDC_INT)

                # check interrupts
                if ints & MSDC_INT_DATTMO:
                    sys.stderr.write("ERROR: Data Timeout\n")
                    sdr_write32(MSDC_INT, ints)
                    sys.exit(1)
                elif ints & MSDC_INT_DATCRCERR:
                    sys.stderr.write("ERROR: Data CRC Error\n")
                    sdr_write32(MSDC_INT, ints)
                    sys.exit(1)

# send mmc command and check response
def msdc_do_command (opcode, arg):

    # build command
    cmd = opcode | MSDC_RESP_R1 << 7 | BLOCK_SIZE << 16
    if opcode == MMC_READ_SINGLE_BLOCK:
        cmd |= (1 << 11)
    elif opcode == MMC_WRITE_BLOCK:
        cmd |= (1 << 11) | (1 << 13)

    # wait until ready
    while sdc_is_busy():
        pass

    # send command
    sdc_send_cmd(cmd, arg)

    cmdsts = MSDC_INT_CMDRDY | MSDC_INT_RSPCRCERR | MSDC_INT_CMDTMO

    while True:

        # poll status
        intsts = sdr_read32(MSDC_INT)
        if (intsts & cmdsts) != 0:

            # ack interrupts
            intsts &= cmdsts
            sdr_write32(MSDC_INT, intsts)

            # check interrupts
            if intsts & MSDC_INT_RSPCRCERR:
                sys.stderr.write("ERROR: Response CRC Error\n")
                sys.exit(1)
            elif intsts & MSDC_INT_CMDTMO:
                sys.stderr.write("ERROR: Command Timeout\n")
                sys.exit(1)

            break

    # get response
    rsp = sdr_read32(MSDC_RESP0)

    # check response
    if rsp & MMC_R1_OUT_OF_RANGE:
        sys.stderr.write("ERROR: Address out of range\n")
        sys.exit(1)
    elif rsp & 0xffff0000:
        sys.stderr.write("ERROR: Unknown error in response\n")
        sys.exit(1)

# get string from mmc device
def get_string (addr, length):

    output = ""
    words = []

    # compute mmc blocks
    mmc_addr = int(addr / BLOCK_SIZE)
    mmc_size = int(length / BLOCK_SIZE)

    # walk address range
    for offset in range(mmc_size):

        # read block data
        msdc_do_command(MMC_READ_SINGLE_BLOCK, mmc_addr + offset)
        block_data = msdc_pio_read(BLOCK_SIZE)
        words += block_data

    # int array to string
    for word in words:
        try:
            output += struct.pack('@I', word).decode()
        except UnicodeDecodeError:
            pass

    return output

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
    print("Extracting build.prop...")

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

    # look for fireos version
    build_prop = get_string(buildprop_addr, buildprop_size)
    for line in build_prop.split("\n"):

        if line.startswith("ro.build.version.fireos="):

            # extract version
            version = line.split("=")[1]

            # check if rootable
            if version == check_version:
                break
            else:
                print("This device is not rootable (version = {0})".format(version))
                sys.exit(1)

    # we didn't find version
    else:
        sys.stderr.write(
            "ERROR: Extracted data does not contain build.prop\n")
        sys.exit(1)

    print("FireOS version ok, device is rootable!")

    # reload saved addr
    last_addr = 0
    if os.path.exists("lastaddr.txt"):
        with open("lastaddr.txt", 'r') as fin:
            last_addr = int(fin.read(), 0)

    # patch file patterns
    patch_list = sorted(glob.glob("patch_*.img"))
    patch_regex = re.compile(r'patch_([0-9a-f]+)\.img')

    # check patch list
    if len(patch_list) == 0:
        sys.stderr.write("ERROR: No patch files were found\n")
        sys.exit(1)

    # process patch files
    for patch in patch_list:

        print("Patching {0}...".format(patch))

        # extract address
        match = patch_regex.match(patch)
        if not match:
            sys.stderr.write(
                "ERROR: '{0}' does not match expected pattern\n".format(patch))
            sys.exit(1)

        patch_addr = int(match.group(1), 16)
        addr = int(patch_addr / BLOCK_SIZE)             # block addr
        size = int(os.path.getsize(patch) / BLOCK_SIZE) # num blocks

        # check patch addr
        if patch_addr < SYSTEM_ADDR:
            sys.stderr.write("ERROR: Patch address is out of range\n")
            sys.exit(1)

        # apply patch file
        with open(patch, 'rb') as fpatch:

            # walk address range
            for offset in range(size):

                phys_addr = (addr + offset) * BLOCK_SIZE
                print("Addr: " + hex(phys_addr))

                # read block from file
                block_data = []
                for _ in range(BLOCK_SIZE >> 2):
                    word = struct.unpack('@I', fpatch.read(4))[0]
                    block_data.append(word)

                # check for resume
                if last_addr >= phys_addr:
                    print("...Already done")
                    continue

                # write block data
                msdc_do_command(MMC_WRITE_BLOCK, addr + offset)
                msdc_pio_write(block_data)

                # save addr to file
                with open("lastaddr.txt", 'w') as fout:
                    fout.write(hex(phys_addr))

    # all done!
    print("Congrats, rooting complete!")

# vim: ai et ts=4 sts=4 sw=4
