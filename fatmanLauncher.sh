#!/bin/sh
# fatmanLauncher.sh
# navigate to home directory, then to PySNAC directory, then wait for pulseaudio/setup, then execute fatman.py, then power off

cd /
cd home/pi/PySNAC
sleep 20
sudo python3 fatman.py
sudo poweroff
