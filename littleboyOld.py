import socket
import threading
import pyaudio
import wave
import sys
import time
import queue
import json
#import lz4 # compression library
#import gzip #compression library
import Adafruit_CharLCD as LCD #LCD library
from LCD_Control import LCD_Control #LCD library

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
                time.sleep(.005)  #trying to slow down this thread
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
    #s = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
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
        while(callInProgress):#for i in range(0, int(RATE/Talk_CHUNK*RECORD_SECONDS)):
            
            data  = stream.read(Talk_CHUNK)
            compressed_data = oc.encode(data)
            encrypted = listen_secret_box.encrypt(compressed_data,nonce)#nonce
            if(len(encrypted)==168):
                bytes_sent = s.send(encrypted)
            time.sleep(.01)  
    except Exception:
        print("problem occured",sys.exc_info()[0])
        
     

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


    PORT = 50007#23555#50007 changed to 50007 from 50008             # Arbitrary non-privileged port
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    #s = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)

    s.bind(('', PORT))
    s.listen(1)


    #caller = threading.Thread(target=call)
    #caller.start()
    
    conn, addr = s.accept()#here the thread waits for a connection
    global waitingForCall
    if waitingForCall :
        if(conn):
            waitingForCall = False
            talker = threading.Thread(target=talk)
            talker.start()

    print ('Connected by', addr)
    time.sleep(2)
    data = conn.recv(Listen_CHUNK)# #1024
    #might need this ? nonce = nacl.utils.random(nacl.secret.SecretBox.NONCE_SIZE)
    i=1
    print("first data received")
    print(len(data))

    writer.start()
    #https://github.com/pyca/pynacl/blob/51acad0e34e125378d166d6bb9662408056702e0/tests/test_public.py
    #alice_box = Box(skalice, pkbob)
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
            data = conn.recv(Listen_CHUNK)# #1024
            i=i+1
        except Exception:
            print("Error warning:",sys.exc_info()[0])
            print("length of shit data",len(data))
            data = conn.recv(Listen_CHUNK-len(data))# throwing away this god awful derter
            #talk_secret_box = nacl.secret.SecretBox(shared_secret)
            
            time.sleep(.05)
            data = conn.recv(Listen_CHUNK)# #1024
            if(not callInProgress):
                break
            continue
            #break
            
    listener_stream.stop_stream()
    listener_stream.close()
    p.terminate()
    conn.close()
    callInProgress=False
    print("listen stopped")
    
def call():
    myInput = control.getUserInput()
    global waitingForCall
    global callInProgress
    controlEnd = LCD_Control(LCD)
    if waitingForCall:
        waitingForCall  = False
        #talk()
        talker = threading.Thread(target=talk)
        talker.start()
        myInput = controlEnd.getUserInput()
        callInProgress=False
        print("call ended")
    else:
        print("call ended")
        callInProgress=False
    print("call stopped")

while(True):
    
    intf = 'wlan0'
    intf_ip = subprocess.getoutput("ip address show dev " + intf).split()
    intf_ip = intf_ip[intf_ip.index('inet')+1].split('/')[0]

    from firebase import firebase
    firebase = firebase.FirebaseApplication('https://pysnac.firebaseio.com',None)

    littleboyIP= firebase.put(url = 'https://pysnac.firebaseio.com', name = '/littleboy/ip',data = intf_ip)
    fatmanIP = firebase.get('/fatman/ip',None)
    #encryption
    #encryption_key = (12345).to_bytes(32,byteorder='big')
    #length = 32
    #shared_secret = encryption_key
    #some public key stuff
    skbob = PrivateKey.generate()
    pkbob = skbob.public_key
    pkalice = HexEncoder.encode(bytes(pkbob))
    frozen = jsonpickle.encode(pkalice)
    firebase.put(url = 'https://pysnac.firebaseio.com', name = '/littleboy/pk',data = frozen)
    nonce = nacl.utils.random(nacl.secret.SecretBox.NONCE_SIZE)
    nonce2 = nacl.utils.random(Box.NONCE_SIZE)
    #audio setup
    #Talk_CHUNK = 1024 
    #Listen_CHUNK = 2088
    #CHANNELS = 1
    RECORD_SECONDS = 80000
    FORMAT = pyaudio.paInt16
    #RATE = 28000
    #WIDTH = 2

    #opus constants
    Talk_CHUNK = 960#2880#1920#2880#4800#3840#4800#960#2880
    Listen_CHUNK = 168#424#168#424 # len of encrypted packet at 48000 is 168, 24000 is 176
    CHANNELS = 1
    RATE = 48000#24000#48000 #24000 is also ok, but need to change opus.py if changed
    WIDTH = 2

    oc = OpusCodec()    #ALSA 7843 underrun causing static?

    #silence = chr(0)*Listen_CHUNK

    #network
    Listener_HOST = fatmanIP#littleboyIP #'172.23.39.163'#'172.23.48.9'#'127.0.0.1'#'192.168.1.19'    # The remote host
    Listener_PORT = 50008#50007#23555#50007              # The same port as used by the server
    #global variable to see whether call was made or received
    waitingForCall = True
    #global variable to see if call has finished
    callInProgress = True
    #Initializing LCD control
    control = LCD_Control(LCD)

    listener_stream = 0
    jitter_buf = Queue()

    writer = threading.Thread(target=write_to_stream)

    listener =threading.Thread(target=listen)
    listener.start()
    caller = threading.Thread(target=call)
    caller.start()
    
    while(callInProgress):
        time.sleep(5)
    print("program restarted")

