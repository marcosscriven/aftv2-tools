#!/bin/bash
###########################################################################
#
# Authors:
# @Aboshi
#
# Thanks to:
# @zeroepoch
# @rbox
# @ImCoKeMaN
# @xenoglyph
#
#
# This script is distributed under the terms of the GNU General Public
# License ("GPL") version 3, as published by the Free Software Foundation.
###########################################################################


# stop script on errors
set -e

# mount sdcard1 with read write premissions
mount -o rw,remount "/storage/sdcard1"
echo "Micro SD Card Mounted With Read/Write Permissions"
echo ""
# allow busybox execution
chmod 775 busybox

PROG=./busybox
FILENAME=verify

# preform md5sum on all files against verify.md5 (5.0.4)
echo "Verifying root.sh busybox boot.img lk.img preloader.img recovery.img system.root.img"
echo ""
echo "Checking: ${FILENAME}.md5"
echo "File Hashes: $(./busybox wc -l ${FILENAME}.md5)"
time ${PROG} md5sum -c "${FILENAME}.md5"
echo "All files verified."

# user must select yes or no
echo "Do You Want To Proceed? There Is No Going Back!"
select yn in "Yes" "No"; do
    case $yn in
        Yes ) break;;
        No ) exit;;
    esac
done

# flushing dalvik cache
echo "Flushing Dalvik-Cache"
rm -rf /data/dalvik-cache/*
echo "Dalvik-Cache Has Been Flushed"

# time to overwrite all system files
echo "**SYSTEM WILL REBOOT WHEN FINISHED**"
echo ""
echo 0 > /sys/block/mmcblk0boot0/force_ro
echo "Copying preloader.img"
dd if=preloader.img of=/dev/block/mmcblk0boot0
echo "Finished"
echo ""
echo 1 > /sys/block/mmcblk0boot0/force_ro
echo "Copying lk.img"
dd if=lk.img of=/dev/block/platform/mtk-msdc.0/by-name/lk
echo "Finished"
echo ""
echo "Copying recovery.img"
dd if=recovery.img of=/dev/block/platform/mtk-msdc.0/by-name/recovery bs=1m
echo "Finished"
echo ""
echo "Copying boot.img"
dd if=boot.img of=/dev/block/platform/mtk-msdc.0/by-name/boot bs=1m
echo "Finished"
echo ""
echo "**PLEASE WAIT THIS WILL TAKE A FEW MINUTES**"
echo "Copying system.root.img"
dd if=system.root.img of=/dev/block/platform/mtk-msdc.0/by-name/system bs=1m
echo "Finished"
echo ""
echo "**Syncing System Please Wait**"
${PROG} sync
echo "Sync Complete!"
echo "Prepare For System Reboot In 60 Seconds"
sleep 60
reboot
