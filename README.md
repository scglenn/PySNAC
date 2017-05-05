# PySNAC - Secured Network Audio Communication

PySNAC is a voice over ip (VOIP) application developed using Python3 on a Raspberry Pi 3 running Raspbian.
Using this software will allow two users to talk to each other on a secured and encrypted internet connection.

# Getting Started
## Hardware Requirements
Two devices are required each utilizing:
- Raspberry Pi 3
- USB Soundcard
- Raspberry Pi Compatible LCD
### USB soundcard
- Hardware: https://www.amazon.com/Plugable-Headphone-Microphone-Aluminum-Compatibility/dp/B00NMXY2MO
#### Must change default soundcard 
edited /usr/share/alsa/alsa.conf to change 0 to 1 in

    defaults.ctl.card 1
    
    defaults.pcm.card 1

### LCD screen
  AdaFruit 16x2 LCD 
- Hardware: https://www.adafruit.com/product/1110
- Library: https://github.com/adafruit/Adafruit_Python_CharLCD
#### It is important to note that the I2C bus must be enabled on your Pi to use the LCD, to do so: 
- Run sudo raspi-config 
- Use the down arrow to select 9 Advanced Options.
- Arrow down to A7 I2C .
- Select yes when it asks you to enable I2C.
- Also select yes when it tasks about automatically loading the kernel module.
- Use the right arrow to select the <Finish> button.
- Select yes when it asks to reboot.

## Software Requirements and Setup
Make sure to have Python3 and Pip3 installed.

    sudo apt-get install python3-dev

    sudo apt-get install python3-pip

    pip3 install pynacl


### Pulse Audio
Run:

    sudo apt-get install python-pyaudio python3-pyaudio

    sudo nano /etc/asound.conf

    Pulseaudio --start

  - put the following in the file and save pcm.!default { type hw card 1 } ctl.!default { type hw card 1 }

  - edited /usr/share/alsa/alsa.conf to change 0 to 1 in
        -defaults.ctl.card 1
        -defaults.pcm.card 1    


### LipSodium
[Installation Instructions link](https://https://download.libsodium.org/doc/installation/)

## Usage

To launch the application run:

    python3 littleboy.py

on one of the Raspberry Pi's then run:

    python3 fatman.py

on the other Raspberry Pi.

Once the LCD display is up  select the check mark on using the buttons on the LCD to initiate the call.
