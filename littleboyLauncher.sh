#!/bin/sh
# littleboyLauncher.sh
# navigate to home directory, then to PySNAC directory, then wait for pulseaudio/setup, then execute littleboy.py, then power off

cd /
cd home/pi/PySNAC
sleep 10
sudo python3 littleboy.py
sleep 30
sudo shutdown now
