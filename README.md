# PySNAC - Secured Network Audio Communication

PySNAC is a voice over ip (VOIP) application developed using Python3 on a Raspberry Pi 3 running Raspbian.
Using this software will allow two users to talk to each other on a secured and encrypted internet connection.

## Getting Started

These hardware components are needed:

  Two Raspberry Pi 3

  Two USB soundcards

  Two LCD screens

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
