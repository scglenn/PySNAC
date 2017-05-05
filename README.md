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
- Text entry was not necessary in the final implementation but for interested users, the file LCD_Control contains a class for users to enter a 15 character string using the directional buttons on the LCD shield [https://github.com/scglenn/PySNAC/blob/master/LCD_Control.py] 
#### It is important to note that the I2C bus must be enabled on your Pi to use the LCD, to do so: 
- Run sudo raspi-config 
- Use the down arrow to select 9 Advanced Options.
- Arrow down to A7 I2C .
- Select yes when it asks you to enable I2C.
- Also select yes when it tasks about automatically loading the kernel module.
- Use the right arrow to select the <Finish> button.
- Select yes when it asks to reboot.

## Software Requirements and Setup
#### Make sure to have Python3 and Pip3 installed.

    sudo apt-get install python3-dev

    sudo apt-get install python3-pip

    pip3 install pynacl

### LibSodium
- Utilized for providing necessary encryption
- PyNaCl is the python wrapper for LibSodium
- [Installation Instructions link](https://https://download.libsodium.org/doc/installation/)

### Pulse Audio
Run:

    sudo apt-get install python-pyaudio python3-pyaudio

    sudo nano /etc/asound.conf

    Pulseaudio --start

#### Underrun issues may occur, remove the ; before the following lines in etc/pulse/daemon.conf and change them to:

    default-fragments = 5
    
    default-fragment-size-msec = 2


### Json Pickle
Json Pickle was used for stringifying objects sent to firebase (The public key for encryption) 

Library installation and usage can be found here: https://github.com/jsonpickle/jsonpickle

### FireBase Layout
 We utilized firebase to exchange the IPs of the two Pis 
- Setup a database on firebase and exchange our credentials for your own modeling after the following to avoid code conflicts

![Alt text](https://github.com/scglenn/PySNAC/blob/master/18318341_1862662593974292_1004394085_o.png?raw=true)
## Usage

To launch the application run:

    python3 littleboy.py

on one of the Raspberry Pi's then run:

    python3 fatman.py

on the other Raspberry Pi.

Once the LCD display is up  select the check mark on using the buttons on the LCD to initiate the call.
