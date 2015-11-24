Prereqs

Thank zeroepoch for the process and not obfuscating the code =) porting couldn't have been done without the base process



Get the images and save them to the same folder you extract this (aftv2-tools):
http://download.zeroepoch.com/aftv2/5.0.3.1/system.root.img.gz
http://download.zeroepoch.com/aftv2/5.0.3.1/system.diff.gz
(I use 7zip to unzip the .gz files in windows: http://www.7-zip.org/ )

Install Python
https://www.python.org/downloads/
get 3.5
allow it to configure path for next step or you will have to run from the python folder


Install pyserial
After installing Python run bat file:
install_pyserial.bat

or manually From command prompt:
python -m pip install pyserial

Thanks to this link at stackoverflow for listing windows com ports:
http://stackoverflow.com/questions/12090503/listing-available-com-ports-with-python

Install VCOM drivers:
the .inf file i used is in this folder, but here are the instructions:
http://thebroodle.com/microsoft/windows/how-to-install-mtk65xx-preloader-usb-vcom-drivers-in-windows/#arvlbdata

You should hear the usb sound when powering on the aftv2 within 5 seconds, if not you'll have to try again.  Also, you should be able to see the com port from there for a short period if the drivers installed correctly.
It may be necessary to catch the new device while booting to install drivers using the steps in the site above (right click install inf will not be enough)


DD for win, is already in this folder, and should just work with the exe in the ported script:
GNU license included in the zip downloaded from: http://www.chrysocome.net/dd




Steps:
plug in a-a cable, but not power to aftv2

Run handshake_win.py
it will list current com ports
as MT preloader is found a new port will be listed and it will attempt the handshake

Note this com port and edit the following line in write_mmc_win.py to match your com port:

PORT       = "COM20"

After that file is edited if your device is still connected on the same com port you are ready to run the bat file:

patch_mmc_win.bat

wait 2 hours like linux root process.... if all goes well.... profit!!


If you want to do the adb steps to disable updates using the a-a cable you can install the kindle drivers manually:
http://forum.xda-developers.com/showthread.php?t=2544410

Otherwise you should be able to do adb via the network if you have that connected


Also, if you want the full aftv2 tools from zeroepoch you can get them from windows too, that's what I used to do the porting:
 to get the tools via windows machine:
https://gitlab.com/zeroepoch/aftv2-tools
 click download, extract zip to folder aftv2-tools 


