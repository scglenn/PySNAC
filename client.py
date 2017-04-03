import socket
import pyaudio
import wave
import sys
import time
import nacl.secret
import nacl.utils
#from hashlib import blake2b
import opuslib
# import ctypes

key = (12345).to_bytes(32,byteorder='big')
box = nacl.secret.SecretBox(key)
#message = b"Audio decryption data"
nonce = nacl.utils.random(nacl.secret.SecretBox.NONCE_SIZE)
print(nonce)
#encrypted = box.encrypt(message,nonce)

#record
CHUNK = 1024 #was 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE =28000
RECORD_SECONDS = 80
#opus data rate 25 millisecond packets
# 10 - 60 ms typical voip
#WebRTC rather than peer2peer
#poster for modern marvel, oral report 15 min, documentation, test report
#last class ethics excercise

HOST = '172.17.42.158'#para Richard
PORT = 50007#23555#50007              # The same port as used by the server

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((HOST, PORT))
#time.sleep(1)
p = pyaudio.PyAudio()

stream = p.open(format=FORMAT,
                channels=CHANNELS,
                rate=RATE,
                input=True,
                frames_per_buffer=CHUNK)

print("*recording")

frames = []
# print(ctypes.c_int())
# create encoder
encoder = opuslib.api.encoder.create(RATE, CHANNELS, opuslib.api.constants.APPLICATION_AUDIO)
try:
    for i in range(0, int(RATE/CHUNK*RECORD_SECONDS)):
     data  = stream.read(CHUNK)
     #frames.append(data)
     # compress here
     #print(str(data))
     #strData = str(data)
     #def encode(encoder, pcm, frame_size, max_data_bytes):
     data = opuslib.api.encoder.encode(encoder, data, CHUNK, RATE*CHUNK)
     encrypted = box.encrypt(data,nonce)#was data,nonce ##added for encrypt boiii
     #print(len(encrypted))
     #print(encrypted)
     if len(encrypted)!=1448:
         s.sendall(encrypted)#was data
except Exception:
    print("problem occured",sys.exc_info())



print("*done recording")

stream.stop_stream()
stream.close()
p.terminate()
s.close()

print("*closed")
