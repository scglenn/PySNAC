import socket
import threading
import pyaudio
import wave
import sys
import time
import lz4 # compression library

import Adafruit_CharLCD as LCD #LCD library
from LCD_Control import LCD_Control #LCD library

import nacl.secret
import nacl.utils

import subprocess
from queue import *
#from requests import get

#import urllib
#external_ip = urllib.request.urlopen('http://ident.me').read().decode('utf8')
#print(external_ip)
#intf_ip = external_ip
#intf_ip = get('https://api.ipify.org').text

intf = 'wlan0'
intf_ip = subprocess.getoutput("ip address show dev " + intf).split()
intf_ip = intf_ip[intf_ip.index('inet')+1].split('/')[0]

from firebase import firebase
firebase = firebase.FirebaseApplication('https://pysnac.firebaseio.com',None)
littleboyIP = firebase.get('/littleboy',None)
fatmanIP = firebase.put(url = 'https://pysnac.firebaseio.com', name = '/fatman',data = intf_ip)

#encryption
encryption_key = (12345).to_bytes(32,byteorder='big')
length = 32
listen_secret_box = nacl.secret.SecretBox(encryption_key)
talk_secret_box = nacl.secret.SecretBox(encryption_key)
nonce = nacl.utils.random(nacl.secret.SecretBox.NONCE_SIZE)

#audio setup
Talk_CHUNK = 1024 
Listen_CHUNK = 2088
CHANNELS = 1
RECORD_SECONDS = 80
FORMAT = pyaudio.paInt16
RATE = 28000
WIDTH = 2

#network
Listener_HOST = littleboyIP #'172.23.39.163'#'172.23.48.9'#'127.0.0.1'#'192.168.1.19'    # The remote host
Listener_PORT = 50007#23555#50007              # The same port as used by the server
#global variable to see whether call was made or received
waitingForCall = True

#Initializing LCD control
control = LCD_Control(LCD)

listener_stream = 0
jitter_buf = Queue()

def write_to_stream():
    global listener_stream
    while(True):
        
        item = jitter_buf.get()
        if( (not item is None) and (jitter_buf.qsize()<=5)):
            listener_stream.write(item)

writer = threading.Thread(target=write_to_stream)

# client thread
def talk():
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
    
    try:
        for i in range(0, int(RATE/Talk_CHUNK*RECORD_SECONDS)):
         data  = stream.read(Talk_CHUNK)
         compressed_data = lz4.dumps(data)#compressed
         
         encrypted = listen_secret_box.encrypt(compressed_data,nonce)#was data,nonce ##added for encrypt boiii
         print(len(encrypted))
         if len(encrypted)!=1448:
             s.sendall(encrypted)#was data
    except Exception:
        print("problem occured",sys.exc_info()[0])
        
     

    print("*done recording")

    stream.stop_stream()
    stream.close()
    p.terminate()
    s.close()

    print("*closed")
    

   
# server thread   
def listen():
    global listener_stream

    p = pyaudio.PyAudio()
    listener_stream = p.open(format=p.get_format_from_width(WIDTH),
                    channels=CHANNELS,
                    rate=RATE,
                    output=True,
                    frames_per_buffer=Listen_CHUNK)


    PORT = 50008#23555#50007 changed to 50007 from 50008             # Arbitrary non-privileged port
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    #s = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)

    s.bind(('', PORT))
    s.listen(1)


    caller = threading.Thread(target=call)
    caller.start()
    
    conn, addr = s.accept()#here the thread waits for a connection
    global waitingForCall
    if waitingForCall :
        if(conn):
            waitingForCall = False
            talker = threading.Thread(target=talk)
            talker.start()

    print ('Connected by', addr)
    time.sleep(2)
    data = conn.recv(Listen_CHUNK, socket.MSG_WAITALL) #1024
    nonce = nacl.utils.random(nacl.secret.SecretBox.NONCE_SIZE)
    i=1
    print("first data received")
    print(len(data))

    writer.start()

    while data != '':
        try:
            data = talk_secret_box.decrypt(data)
            data = lz4.loads(data)#decompress
            jitter_buf.put(data)
            print(jitter_buf.qsize())
            #stream.write(data)
            data = conn.recv(Listen_CHUNK, socket.MSG_WAITALL) #1024
            i=i+1
            #print(i)
           
        except Exception:
            print("no connection",sys.exc_info())
            break
            
    stream.stop_stream()
    stream.close()
    p.terminate()
    conn.close()
    
def call():
    myInput = control.getUserInput()
    global waitingForCall
    if waitingForCall:
        waitingForCall  = False
        talk()

    
listener =threading.Thread(target=listen)
listener.start()

