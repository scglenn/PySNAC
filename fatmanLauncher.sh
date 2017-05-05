#!/bin/sh
# fatmanLauncher.sh
# navigate to home directory, then to PySNAC directory, then wait for pulseaudio/setup, then execute littleboy.py, then power off

cd /
cd home/pi/PySNAC
sleep 10
sudo python3 fatman.py
sleep 30
sudo shutdown now
