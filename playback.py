import struct
import numpy as np
import sounddevice as sd
import time
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

    #Run only when new song is started
    isResumed = True
    if(resumeTime == 0):
        startTime = time.time()
        playTime = dataSize/(samples*channel*1.0) 

        return startTime, playTime, isResumed
    
           

def main():
    poweredOn = True

    #Loops while player is active
    while(poweredOn):
        timeStopped = 0
        goodChoice = False

        #Handles input of song and speed and decodes the WAV file
        while(not goodChoice):
            try:
                file = input("Choose song: ")
                speed = float(input("set speed: "))

                if(0.1 <= speed and speed <= 5 and speed != 0):
                    audio, samples, channel = decode_wav(file)
                    goodChoice = True

                else:
                    print("Please select a valid speed")

            except:
                print("Song could not be found!")
                goodChoice = False

        #Plays the audio
        startTime, playTime, isResumed = play_audio(speed, audio, samples, channel)
        currentlyPlaying = True

        #Controls for the audio player
        while(currentlyPlaying):
            choice = input("p for Pause, r to Resume or s to Stop")

            #Saves the current resumeTime taking into account the startTime and timeStopped
            if(choice == "p" and isResumed):
                resumeTime = time.time()-startTime-timeStopped
                sd.stop()
                stopTime = time.time()
                isResumed = False

            #Resumes the playback taking and calculating how long playback was paused
            if(choice == "r" and not isResumed):
                play_audio(speed, audio, samples, channel, resumeTime)
                timeStopped = timeStopped + (time.time()-stopTime)
                stopTime = 0
                isResumed = True

            #Stops the playback 
            if(choice == "s"):
                sd.stop()
                currentlyPlaying = False

            #Checks if music has stopped playing taking into account timeStopped
            if(playTime+timeStopped < time.time() - startTime):
                currentlyPlaying = False
        
        #Checks if user wants to play another song or turn off the player
        anotherSong = input("Do you want to play another song? (y/n)")
        if(anotherSong == "n"):
            poweredOn = False


if __name__ == "__main__":
    main()