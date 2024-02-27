import struct
import numpy as np
import sounddevice as sd
import math

# H = unsigned short (2 byte), I = unsigned int (4 byte) 
# Get the wav header information
def getProperties(file):
    with open(file, 'rb') as audioInfo:
        # read the header of the file
        header = audioInfo.read(44)
        riff = header[0:4]
        fmt = header[12:16]
        data = header[36:40]

        # check if the file is a valid wav file
        status = True
        if riff != b'RIFF' or fmt != b'fmt ' or data != b'data':
            return 0, 0, 0, 0, False
        
        # get the properties of the file
        numChannels = struct.unpack('<H', header[22:24])[0]
        sampleRate = struct.unpack('<I', header[24:28])[0]
        bitsPerSample = struct.unpack('<H', header[34:36])[0]
        subchunk2Size = struct.unpack('<I', header[40:44])[0]

    return numChannels, sampleRate, bitsPerSample, subchunk2Size, status


def getDuration(file)->float:
    # get the properties of the file
    numChannels, sampleRate, bitsPerSample, subchunk2Size, status = getProperties(file)

    # calculate the duration
    # data size of the "data" subchunk = numSamples * numChannels * bitsPerSample / 8
    # by the information of the header, we can calculate the duration by
    # dividing the data size by the product of the sample rate, number of channels, and bits per sample
    duration = subchunk2Size*8 / (sampleRate * numChannels * bitsPerSample)

    return duration

#Decodes the WAV file
# it will returning a 16-bit integer array, sample rate, and number of channels
def decode_wav(file):
    with open(file,'rb') as audioInfo:
        #The first 44 bytes store the header information
        header = audioInfo.read(44)

        #Use the headers to find the amount of channels and the sample rate
        amountOfChannels = struct.unpack('<H', header[22:24])[0]
        sampleRate = struct.unpack('<I', header[24:28])[0]

        #Reads data after 44 Byte where audio data is stored
        audioInfo.seek(44)
        data = audioInfo.read()

        #Converts the raw byte data into int16 array
        audio_data = np.frombuffer(data, dtype=np.int16)

    return audio_data, sampleRate, amountOfChannels

# it will returning a raw data, sample rate, and number of channels
def decode2Raw(file):
    with open(file,'rb') as audioInfo:
        #The first 44 bytes store the header information
        header = audioInfo.read(44)

        #Use the headers to find the amount of channels and the sample rate
        amountOfChannels = struct.unpack('<H', header[22:24])[0]
        sampleRate = struct.unpack('<I', header[24:28])[0]

        #Reads data after 44 Byte where audio data is stored
        audioInfo.seek(44)
        data = audioInfo.read()

    return data, sampleRate, amountOfChannels

def play_audio(speed, audio, samples, channel, resumeTime = 0):

    #Resumes the audio file from the resumeTime
    if(resumeTime != 0):
        dataResume = resumeTime*(samples*channel*speed)
        audio = audio[math.floor(dataResume):]

    #Trims the data to ensure it is divisible by numer of channels and can be reshaped
    dataSize = len(audio)
    sampleSize = dataSize // channel * channel
    if sampleSize != dataSize:
        audio = audio[:sampleSize]

    #Handles 2 or more channels
    audio = audio.reshape((-1, channel))

    #Play the audio file taking playback speed in regard
    sd.play(audio, samples*speed)