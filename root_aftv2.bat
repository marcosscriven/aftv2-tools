@echo off

echo Starting the AFTV2 rooting process
echo 1. Connect your PC to the AFTV2 with an A-male to A-male USB cable
echo 2. Power on / power cycle the AFTV2 to initiate the preloader
echo.

root_aftv2.exe

if errorlevel 0 (
    echo Power cycle the AFTV2 to finish the rooting process
) else (
    echo The rooting process has FAILED!
)

pause
