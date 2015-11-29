@echo off

set BASE_ADDR=0x00000000058e0000

call :versioncheck
Echo Done!
pause
exit /b

:versioncheck
    set ADDR=0x4B4EC000
    set LENGTH=512
    set trimaddr=%ADDR:~2%
    set TMP_FILE=ver_%trimaddr%.img
	
    echo Reading version %TMP_FILE%...
	set /a ADDR=%ADDR% + 0
    rem # extract patched region
    rem dd if=%BASE_IMG% of=%TMP_FILE% bs=1 skip=%ADDR% count=%LENGTH%

    set /a PHYS_ADDR= %BASE_ADDR% + %ADDR%

    rem # Read version info
    read_mmc_win.py %PHYS_ADDR% %LENGTH% %TMP_FILE%
    find "5.0.3.1 (534011720)" %TMP_FILE% 
    rem # Version check success?
	    if  %errorlevel% GEQ 1 (
		echo error %errorlevel% Version check failed!
		pause
		exit %errorlevel%
	) 
	else (
		echo Version check passed!
	)
	
    echo.
	exit /b

rem vim: ai et ts=4 sts=4 sw=4
