import pyaudio
import wave
import time
import sys
from opus import OpusCodec

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
    origFrameSize = len(frames)
    #encode
    print("creating OpusCodec...")
    oc = OpusCodec()
    print("starting encoding, decoding, and writing...")
    enTime = 0
    decTime = 0
    enSize = 0
    decSize = 0
    chunkSize = 2*960
    with wave.open(sys.argv[2], 'w') as fileOut:
        fileOut.setparams(params)
        for i in range(int(len(frames)/chunkSize)):
            # encoding + metrics
            enStart = time.time()
            enData = oc.encode(frames)
            enTime += time.time()-enStart
            enSize += len(enData)
            # decoding + metrics
            decStart = time.time()
            decData = oc.decode(enData)
            decTime = time.time()-decStart
            decSize += len(decData)
            # writing and resizing of frames
            fileOut.writeframes(decData)
            frames = frames[chunkSize:]
        print("finished encoding, decoding, and writing")
        fileOut.close()
    print("\ttotal encoding time: " + str(enTime) + " seconds\n\ttotal decoding time: " + str(decTime) + " seconds")
    print("metrics:\n\tcompressed file size vs. original: " + str(enSize/origFrameSize*100) + "%\n\toverall reduction: " + str(100 - (decSize/origFrameSize*100)) + "%")
    fileIn.close()
    print("test complete")
