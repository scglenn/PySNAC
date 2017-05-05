import socket
import threading
import pyaudio
import wave
import sys
import time
import queue
import json
import os
import Adafruit_CharLCD as LCD
from LCD_Control import LCD_Control

import nacl.secret
import nacl.utils
from nacl.public import PrivateKey, PublicKey,Box
from nacl.encoding import HexEncoder
import jsonpickle
secretNotKnown = True

import subprocess
from queue import *
from opus import OpusCodec

def write_to_stream():
    global listener_stream
    global callInProgress
    while(callInProgress):
        try:
            item = jitter_buf.get()
            if (not item is None) and (jitter_buf.qsize() <= 5):
                listener_stream.write(item)
                time.sleep(.005)  #slows down this thread
        except Exception:
            print("write to stream error:",sys.exc_info())
    print("write to stream stopped")
    
# client thread
def talk():
    global shared_secret
    global secretNotKnown
    global nonce2
    global nonce
    global callInProgress
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((Listener_HOST, Listener_PORT))

    p = pyaudio.PyAudio()
    stream = p.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    input=True,
                    frames_per_buffer=Talk_CHUNK)

    print("*recording")
    global skbob
    pkalice = jsonpickle.decode(firebase.get('/fatman/pk',None))
    pkalice = PublicKey(pkalice,encoder=HexEncoder)
    bob_box = Box(skbob, pkalice)
    ####PUBLIC KEY AGREEMENT

    data  = stream.read(Talk_CHUNK)
    compressed_data = oc.encode(data)
    encrypted = bob_box.encrypt(compressed_data, nonce2)
    s.send(encrypted)
    ####PUBLIC KEY AGREEMENT
    while secretNotKnown:
        time.sleep(.01)
    #nonce = nacl.utils.random(nacl.secret.SecretBox.NONCE_SIZE)
    listen_secret_box = nacl.secret.SecretBox(shared_secret)
    print("talk",shared_secret)
    forwardsecret=0
    try:
        while(callInProgress):
            
            data  = stream.read(Talk_CHUNK)
            compressed_data = oc.encode(data)
            encrypted = listen_secret_box.encrypt(compressed_data,nonce) #nonce
            if(len(encrypted)==168):
                bytes_sent = s.send(encrypted)
            time.sleep(.01)  
    except Exception:
        print("talk problem occured",sys.exc_info())
        
    stream.stop_stream()
    stream.close()
    p.terminate()
    s.close()
    callInProgress = False
    print("talk stopped")
    
# server thread   
def listen():
    global shared_secret
    global listener_stream
    global secretNotKnown
    global nonce
    global nonce2
    global callInProgress
    p = pyaudio.PyAudio()
    listener_stream = p.open(format=p.get_format_from_width(WIDTH),
                    channels=CHANNELS,
                    rate=RATE,
                    output=True,
                    frames_per_buffer=Listen_CHUNK)


    PORT = 50007 # Arbitrary non-privileged port
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)

    s.bind(('', PORT))
    s.listen(1)
    
    conn, addr = s.accept() # waits for a connection
    global waitingForCall
    if waitingForCall :
        if(conn):
            waitingForCall = False
            talker = threading.Thread(target=talk)
            talker.start()

    control.displayUserInputDuringCall()

    print ('Connected by', addr)
    time.sleep(2)
    data = conn.recv(Listen_CHUNK)
    i=1
    print("first data received")
    print(len(data))

    writer.start()
    global skbob
    pkalice = jsonpickle.decode(firebase.get('/fatman/pk',None))
    pkalice = PublicKey(pkalice,encoder=HexEncoder)
    bob_box = Box(skbob, pkalice)

    data = bob_box.decrypt(data)
    shared_secret = bob_box.shared_key()
    talk_secret_box = nacl.secret.SecretBox(shared_secret)
    print("listen",shared_secret)
    secretNotKnown = False
    data = conn.recv(Listen_CHUNK)
    while data != '' and callInProgress:
        try:
            data = talk_secret_box.decrypt(data)
            data = oc.decode(data)
            jitter_buf.put(data)
            data = conn.recv(Listen_CHUNK)
            i=i+1
        except Exception:
            print("listen error warning: ",sys.exc_info()[0])
            print("length of excepted data: ",len(data))
            if len(data) == 0:
                callInProgress = False
            data = conn.recv(Listen_CHUNK-len(data))            
            time.sleep(.05)
            data = conn.recv(Listen_CHUNK)
            if(not callInProgress):
                break
            continue
            
    listener_stream.stop_stream()
    listener_stream.close()
    p.terminate()
    conn.close()
    callInProgress=False
    print("listen stopped")
    
def call():
    myInput = control.getUserInputInit()
    global waitingForCall
    global callInProgress
    if waitingForCall:
        waitingForCall  = False
        talker = threading.Thread(target=talk)
        talker.start()
        time.sleep(5)
        myInput = control.getUserInput()
        callInProgress=False
        print("call ended")
    else:
        print("call ended2")
        callInProgress=False
    print("call stopped")

oneCall = True
os.system("sudo pulseaudio --start") # starts PulseAudio
while(oneCall):
    oneCall = False
    intf = 'wlan0'
    intf_ip = subprocess.getoutput("ip address show dev " + intf).split()
    intf_ip = intf_ip[intf_ip.index('inet')+1].split('/')[0]

    from firebase import firebase
    firebase = firebase.FirebaseApplication('https://pysnac.firebaseio.com',None)

    littleboyIP= firebase.put(url = 'https://pysnac.firebaseio.com', name = '/littleboy/ip',data = intf_ip)
    fatmanIP = firebase.get('/fatman/ip',None)
    
    skbob = PrivateKey.generate()
    pkbob = skbob.public_key
    pkalice = HexEncoder.encode(bytes(pkbob))
    frozen = jsonpickle.encode(pkalice)
    firebase.put(url = 'https://pysnac.firebaseio.com', name = '/littleboy/pk',data = frozen)
    nonce = nacl.utils.random(nacl.secret.SecretBox.NONCE_SIZE)
    nonce2 = nacl.utils.random(Box.NONCE_SIZE)
    nonceInt = int.from_bytes(nonce,byteorder='little')
    if(not (nonceInt%2)==1):
        nonceInt = nonceInt +1
        nonce = nonceInt.to_bytes(24,byteorder='little')

    RECORD_SECONDS = 80000
    FORMAT = pyaudio.paInt16

    #opus constants
    Talk_CHUNK = 960
    Listen_CHUNK = 168
    CHANNELS = 1
    RATE = 48000
    WIDTH = 2

    oc = OpusCodec()

    #network
    Listener_HOST = fatmanIP # the remote host
    Listener_PORT = 50008 # the same port as used by the server
    # global variable to see whether call was made or received
    waitingForCall = True
    # global variable to see if call has finished
    callInProgress = True
    # Initializing LCD control
    control = LCD_Control(LCD)

    listener_stream = 0
    jitter_buf = Queue()

    writer = threading.Thread(target=write_to_stream)

    listener =threading.Thread(target=listen)
    listener.start()
    caller = threading.Thread(target=call)
    caller.start()
    
    while(callInProgress):
        nonceInt = int.from_bytes(nonce,byteorder='little')
        nonceInt = nonceInt +2
        nonce = nonceInt.to_bytes(24,byteorder='little')
        time.sleep(1)
    control.displayEndMessage()
print("program ended")

