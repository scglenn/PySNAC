# Echo server program
import socket
import pyaudio
#import wave
import time
import sys
# 4 25
import nacl.secret
import nacl.utils
#from hashlib import blake2b
import opuslib

key = (12345).to_bytes(32,byteorder='big')
box2 = nacl.secret.SecretBox(key)

#plaintext = box2.decrypt(encrypted)
#print ("plaintext: %s" % plaintext.decode('ascii'))

'''
import opuslib
import opuslib.api
import opuslib.api.encoder
import opuslib.api.decoder
'''

CHUNK = 2088
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 48000#44100
RECORD_SECONDS = 80#5
WAVE_OUTPUT_FILENAME = "server_output.wav"
WIDTH = 2
DECODE_FEC = 1
frames = []

p = pyaudio.PyAudio()
stream = p.open(format=p.get_format_from_width(WIDTH),
                channels=CHANNELS,
                rate=RATE,
                output=True,
                frames_per_buffer=CHUNK)


HOST = ''                 # Symbolic name meaning all available interfaces
PORT = 50007             # Arbitrary non-privileged port
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((HOST, PORT))
s.listen(1)
conn, addr = s.accept()

print ('Connected by', addr)
#time.sleep(2)
data = conn.recv(CHUNK) #1024
nonce = nacl.utils.random(nacl.secret.SecretBox.NONCE_SIZE)
i=1
print("first data received")
print(len(data))
#time.sleep(1)
#decoder = opuslib.api.decoder.create(RATE, CHANNELS)
while data != '':
    #print(len(data))
    if True:
        try:
            if(len(data) ==2088):
                data = box2.decrypt(data)
                # print(type(data))
                #def decode(decoder, data, length, frame_size, decode_fec, channels=2):
                # data = opuslib.api.decoder.decode(decoder, data, CHUNK, RATE, DECODE_FEC, CHANNELS)
                stream.write(data)
                data = conn.recv(CHUNK) #1024
                i=i+1
                #print(i)
                #print(len(data))
            elif(len(data) <2088):
                #print("Data length was garbage");
                remainingChunk = 2088 - len(data)
                leftover = conn.recv(remainingChunk)
                data += leftover
            else:
                #print("just garbage")
                data = conn.recv(CHUNK)
                #print(len(data))
        except Exception:
            print("problem occured",sys.exc_info()[0])
            break

wf = wave.open(WAVE_OUTPUT_FILENAME, 'wb')
wf.setnchannels(CHANNELS)
wf.setsampwidth(p.get_sample_size(FORMAT))
wf.setframerate(RATE)
wf.writeframes(b''.join(frames))
wf.close()

stream.stop_stream()
stream.close()
p.terminate()
conn.close()
