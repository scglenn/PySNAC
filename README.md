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
- Text entry was not necessary in the final implementation but for interested users, the file LCD_Control in the old subdirectory contains a class for users to enter a 15 character string using the directional buttons on the LCD shield [https://github.com/scglenn/PySNAC/blob/master/old/LCD_Control.py] 
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

### LibSodium
- Utilized for providing necessary encryption
- PyNaCl is the python wrapper for LibSodium
- [Installation Instructions link](https://https://download.libsodium.org/doc/installation/)

    ```
    sudo pip3 install pynacl
    ```

### OpusCodec
- Utilized for compressing audio data pre-encryption and decompressing received post-decryption data
- opuslib is the python wrapper for OpusCodec
- [Installation Instructions link](http://opus-codec.org/downloads/)

    ```
    sudo pip3 install opuslib
    ```

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
 We utilized firebase to exchange the IPs of the two Pis:
 
    sudo pip install requests
    
    sudo pip install python-firebase
    
    sudo pip3 install firebase
    
- Setup a database on firebase and exchange our credentials for your own modeling after the following to avoid code conflicts

![Alt text](https://github.com/scglenn/PySNAC/blob/master/18318341_1862662593974292_1004394085_o.png?raw=true)
## Usage

To launch the application run:

    python3 littleboy.py

on one of the Raspberry Pi's then run:

    python3 fatman.py
    
on the other Raspberry Pi.

Alternatively, the Pi's can be set up to run these scripts on boot. Follow the instructions in the following link using fatmanLauncher.sh for one Pi and littleboyLauncher.sh for the other: [Instructions for adding a start-up script](http://www.instructables.com/id/Raspberry-Pi-Launch-Python-script-on-startup/)

Once the LCD display is up  select the check mark on using the buttons on the LCD to initiate the call.

### Code Information
fatman.py explained

There are 5 threads being run in this scripts

`def write_to_stream()`:
This thread handles the audio being sent to the earbuds as output.
Audio byte data is grabbed from the jitter buffer and written to the output stream.
Audio data is only written to stream if the buffer is below a threshold, this makes it so that the output stream doesn't overflow with too much data but also makes the most recent data heard in order to lower the audio delay. Old data on the buffer is thrown out but because of the small delay this loss of data is only obvious when encountering network problems.

`def talk()`:
This thread is only started when the user makes the call or receives a call.
On start this thread grabs the other user’s IP address and port number.
The ephemeral public key of the other user is grabbed from firebase and the diffie-hellman key exchange occurs. At this point both users now have a shared secret that is used with private key symmetric encryption. 
The call begins by grabbing audio data from the stream -> compressing it -> encrypting it -> and sending the data to the other user.
When the call ends the while loop will break and the stream will close and terminate

`def listen()`:
This thread starts upon starting the script. It sets up the TCP socket and waits for a call and any incoming audio data.
When a call is received the diffie-hellman public key encryption is set up and the shared secret is obtained. 
All audio data is decrypted first and then decompressed.
Once raw data is obtained it is put onto the jitter buffer in order to smooth out audio data being received.
If part of a packet is received the thread will wait for the other part of the audio data to be received and throw it away in order to shift the incoming data over for correct decryption
When the call is finished the stream is closed and connection terminated.

`def call()`:
This thread is called on starting the script. It waits for user
To hit the select button on the lcd so they can initiate the call. It is also used for ending the call.

start up code:
The rest of the code outside of the threads is called upon starting the thread. It grabs its ip address and sends it to firebase. The other devices ip is grabbed from firebase so it knows the ip that it will be having a conversation with. 
The private and public key is generated. The public key is sent to firebase. Nonce for the symmetric key encryption is generated and the nonce for the public key encryption is generated. The rest is setting up the pi’s compression,variables, and starting threads.


 
Littleboy.py explained
The littleboy.py code is almost exactly the fatman.py code the only difference is that the the port numbers are reversed for sending data out and receiving.


