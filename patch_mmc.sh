#!/bin/bash

# check usage
if [ $# -ne 3 ] ; then
    echo "Usage: $(basename $0) base_addr base_img diff_file"
    exit 1
fi

BASE_ADDR="$1"
BASE_IMG="$2"
DIFF_FILE="$3"

# get changed regions
DIFF_DATA=( $(./changed_blks.py "${DIFF_FILE}") )

# iterate over regions
for I in $(seq 1 2 ${#DIFF_DATA[@]}) ; do

    ADDR="$(( ${DIFF_DATA[$((I - 1))]} ))" # hex->dec
    LENGTH="${DIFF_DATA[$I]}"

    TMP_FILE="patch_$(printf "%08x" "${ADDR}").img"
    echo "Patching ${TMP_FILE}..."

    # extract patched region
    dd if="${BASE_IMG}" of="${TMP_FILE}" bs=1 skip="${ADDR}" count="${LENGTH}"

    PHYS_ADDR="$((BASE_ADDR + ADDR))"

    # apply patch to mmc
    ./write_mmc.py "${PHYS_ADDR}" "${TMP_FILE}"

    # patch success?
    if [ $? -ne 0 ] ; then
        exit 1
    fi

    echo

done

# vim: ai et ts=4 sts=4 sw=4
