import socket
import pyaudio
import wave


import nacl.secret
import nacl.utils
from hashlib import blake2b


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
RATE = 44100
RECORD_SECONDS = 40

HOST = 'localhost'#'192.168.1.19'    # The remote host
PORT = 50007              # The same port as used by the server

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((HOST, PORT))

p = pyaudio.PyAudio()

stream = p.open(format=FORMAT,
                channels=CHANNELS,
                rate=RATE,
                input=True,
                frames_per_buffer=CHUNK)

print("*recording")

frames = []

for i in range(0, int(RATE/CHUNK*RECORD_SECONDS)):
 data  = stream.read(CHUNK)
 frames.append(data)
 #print(str(data))
 #strData = str(data)
 encrypted = box.encrypt(data,nonce)#was data,nonce ##added for encrypt boiii
 print(len(encrypted))
 s.sendall(encrypted)#was data
 

print("*done recording")

stream.stop_stream()
stream.close()
p.terminate()
s.close()

print("*closed")
