#!/bin/sh
# littleboyLauncher.sh
# navigate to home directory, then to PySNAC directory, then wait for pulseaudio/setup, then execute littleboy.py, then power off

cd /
cd home/pi/PySNAC
sleep 20
sudo python3 littleboy.py
sudo poweroff
