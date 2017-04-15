import pyaudio
import wave
import time
import sys
import opuslib

def printParams(params):
    print("channels: " + str(params[0]) + ", type: " + str(type(params[0])))
    print("sampwidth: " + str(params[1]) + ", type: " + str(type(params[1])))
    print("framerate: " + str(params[2]) + ", type: " + str(type(params[2])))
    print("nframes: " + str(params[3]) + ", type: " + str(type(params[3])))
    print("comptype: " + str(params[4]) + ", type: " + str(type(params[4])))
    print("compname: " + str(params[5]) + ", type: " + str(type(params[5])))

if len(sys.argv) != 3:
    print("Usage: encodeDecode [fileIn] [fileOut]")

with wave.open(sys.argv[1], 'r') as fileIn:
    #params has form (nchannels, sampwidth, framerate, nframes, comptype, compname)
    params = fileIn.getparams()
    print("getting params...")
    printParams(params)
    frames = fileIn.readframes(params[3])
    print("length of frames: " + str(len(frames)))
    print("total size of frames: " + str(sys.getsizeof(frames)))
    CHANNELS = params[0]
    #FRAME_SIZE = params[1]
    FRAME_SIZE = 960         #<- from .c example
    MAX_FRAME_SIZE = 6*960     #<- from .c example
    MAX_PACKET_SIZE = (3*1276) #<- from .c example
    FRAME_RATE = params[2]
    BIT_RATE = 16000
    #encode
    print("creating encoder...")
    encoder = opuslib.api.encoder.create(FRAME_RATE, CHANNELS, opuslib.api.constants.APPLICATION_AUDIO)
    opuslib.api.encoder.ctl(encoder, opuslib.api.ctl.set_bitrate, BIT_RATE)
    print("encoding data...")
    #encode(encoder, pcm, frame_size, max_data_bytes):
    enData = opuslib.api.encoder.encode(encoder, frames, FRAME_SIZE, len(frames))
    #decode
    print("encoding done\ncreating decoder...")
    decoder = opuslib.api.decoder.create(FRAME_RATE, CHANNELS)
    opuslib.api.encoder.ctl(decoder, opuslib.api.ctl.set_bitrate, BIT_RATE)
    #decode(decoder, data, length, frame_size, decode_fec, channels=2):
    print("decoding data...")
    #check line 992 in opus decoder.c
    decData = opuslib.api.decoder.decode(decoder, enData, 1000, MAX_FRAME_SIZE, 0, CHANNELS)
    # for q in range(1000000):
    #     try:
    #         decData = opuslib.api.decoder.decode(decoder, enData, q, MAX_FRAME_SIZE, 0, CHANNELS)
    #         print(str(q))
    #     except:
    #         a = "fuck you"
    print("decoding done\nwriting to file...")
    decData = decData
    with wave.open(sys.argv[2], 'w') as fileOut:
        fileOut.setparams(params)
        fileOut.writeframes(decData)
        fileOut.close()
    fileIn.close()
    print("test complete")
