import pyaudio
import wave
import time
import sys
import lz4

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
    frames = fileIn.readframes(params[3])
    #encode
    print("encoding data...")
    start = time.time()
    enData = lz4.block.compress(frames)
    #decode
    print("encoding done, took " + str(time.time() - start) + " seconds")
    print("decoding data...")
    start = time.time()
    decData = lz4.block.decompress(enData)
    print("decoding done, took " + str(time.time() - start) + " seconds")
    print("metrics:\n\tcompression ratio: " + str(len(enData)/len(frames)) + "\n\toverall reduction: " + str(len(decData)/len(frames)))
    print("writing to file...")
    with wave.open(sys.argv[2], 'w') as fileOut:
        fileOut.setparams(params)
        # fileOut.writeframes(enData)
        fileOut.writeframes(decData)
        fileOut.close()
    fileIn.close()
    print("test complete")
