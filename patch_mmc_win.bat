@echo off
rem #!/bin/bash

rem  check usage
rem if [ %3 !=  ] ; then
rem     echo "Usage: $(basename $0) base_addr base_img diff_file"
rem     exit 1
rem fi

set BASE_ADDR=0x00000000058e0000
set BASE_IMG=system.root.img
set DIFF_FILE=system.diff

rem Start program before plugging in device, handshake first..
rem handshake_win.py

rem # get changed regions
changed_blks.py %DIFF_FILE% > changed.txt

rem # iterate over regions
for /f "tokens=1,2" %%A in (changed.txt) do call :subroutine %%A %%B

Echo Done!
pause
exit /b

:subroutine
    set ADDR=%1
    set LENGTH=%2
    set trimaddr=%ADDR:~2%
    set TMP_FILE=patch_%trimaddr%.img
	
    echo Patching %TMP_FILE%...
	set /a ADDR=%ADDR% + 0
    rem # extract patched region
    dd if=%BASE_IMG% of=%TMP_FILE% bs=1 skip=%ADDR% count=%LENGTH%

    set /a PHYS_ADDR= %BASE_ADDR% + %ADDR%

    rem # apply patch to then
    write_mmc_win.py %PHYS_ADDR% %TMP_FILE%

    rem # patch success?
	
    if  %errorlevel% GEQ 1 echo error %errorlevel%
    echo.
	exit /b

rem vim: ai et ts=4 sts=4 sw=4
