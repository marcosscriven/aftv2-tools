Prereqs

1: Thank zeroepoch for the process and not obfuscating the code =) porting couldn't have been done without the base process

2: Get the images and save them to the same folder you extract this (aftv2-tools):
http://download.zeroepoch.com/aftv2/<version>/system.root.img.gz
http://download.zeroepoch.com/aftv2/<version>/system.diff.gz
(I use 7zip to unzip the .gz files in windows: http://www.7-zip.org/ )

3: Install Python
https://www.python.org/downloads/
get 3.5
allow it to configure path for next step or you will have to run from the python folder

4: Install pyserial
After installing Python run bat file:
install_pyserial.bat

or manually From command prompt:
python -m pip install pyserial


5: Install VCOM drivers:
the .inf file i used is in win_drivers, but here are the instructions:
http://thebroodle.com/microsoft/windows/how-to-install-mtk65xx-preloader-usb-vcom-drivers-in-windows/#arvlbdata

Plug the usb a-a cable in to the fire tv and the pc first, then plug in power.
You should hear the usb sound when powering on the aftv2 within 5 seconds, if not you'll have to try again.
Also, you should be able to see the com port in device manager for a short period if the drivers installed correctly.
It may be necessary to catch the new device while booting to install drivers using the steps in the site above (right click install inf will not be enough)


Steps: (Wow, only 3 steps?  - Yes you still have to do the pre-req's!)
1: plug in a-a cable, but not power to aftv2

2: Run handshake.py
It will show:
Waiting for preloader...

At this point plug in power to your AFTV2 and if drivers were installed successfully it should show these lines: (your port may be different)
Found port = COM19
Handshake complete!

Now you are ready to run patch_mmc.bat: (don't unplug anything)
3: Run patch_mmc.bat

wait 2 hours like linux root process.... if all goes well.... profit!!

Note: If it hangs for a long time without changing addresses it is probably stuck.  You can safely restart this process, it will resume.

Aditional info:
If you want to do the adb steps to disable updates using the a-a cable you can install the kindle drivers manually:
http://forum.xda-developers.com/showthread.php?t=2544410

Otherwise you should be able to do adb via the network if you have that connected

DD for win, is already in this folder, and should just work with the exe in the ported script:
Downloaded from: http://www.chrysocome.net/dd, GNU licensed

Thanks to this link at stackoverflow for info on listing windows com ports:
http://stackoverflow.com/questions/12090503/listing-available-com-ports-with-python

Also, if you want the full aftv2 tools from zeroepoch you can get them from windows too, that's what I used to do the porting:
 to get the tools via windows machine:
https://gitlab.com/zeroepoch/aftv2-tools
 click download, extract zip to folder aftv2-tools
