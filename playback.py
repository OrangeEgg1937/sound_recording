import struct
import numpy as np
import sounddevice as sd
import math

# Danny: I chaged the file path to an empty string, so you can set it to your own file path
# also I put a if __name__ == "__main__":, you can debug the file by running it directly
# and change line 56 for the return end time, the GUI timer will handler the speed (you may try it in the GUI)

#Change to your filepath where audio files exist
filepath = ""

#Decodes the WAV file
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