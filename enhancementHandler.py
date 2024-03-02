# unless specifying a different file, this class will handle the enhancement
import clipping

from PyQt5.QtWidgets import QFileDialog, QMainWindow
from PyQt5.QtCore import Qt
from UI.Ui_mainWindow import Ui_mainWindow
from ImportHandler import ImportHandler
from PyQt5.QtCore import QTimer
import noisereduce as nr
import numpy as np
import playback

class EnhancementHandler:

    def __init__(self, ui: Ui_mainWindow, mainWindow: QMainWindow, importHandler: ImportHandler):
        self.ui = ui
        self.mainWindow = mainWindow
        self.importHandler = importHandler
        self.message = ui.enc_message

        # connect the enhancement buttons
        self.ui.pitchChange.clicked.connect(self.__pitchShift)

        # connect the enhancement buttons
        self.ui.noiseRemoveBtn.clicked.connect(self.__noiseRemove)



    def __pitchShift(self):
        # get the file path
        filePath = self.importHandler.getCurrentSelectedFile()

        # check the file path exist or not
        if filePath == "" or filePath == None:
            self.__setMessage("Please select a file first!")
            return

        # get the semitone value
        semitone = self.ui.pitchValue.text()

        # check if the value is valid or not
        if semitone == "" or not semitone.isnumeric():
            self.__setMessage("Please enter a valid value")
            return

        # change the pitch of the file
        clipping.changePitch(filePath, float(semitone))

        # set the player message
        self.__setMessage("Pitch changed, select the file to play!")
    
    def __noiseRemove(self):
        # get the file path
        filePath = self.importHandler.getCurrentSelectedFile()
        self.__setMessage("Processing noise reduction...")

        # check the file path exist or not
        if filePath == "" or filePath == None:
            self.__setMessage("Please select a file first!")
            return

        #remove the noise from the file
        audio, rate, channel = playback.decode_wav(filePath)

        #Trims the data to ensure it is divisible by the number of channels and can be reshaped
        data_size = len(audio)
        sample_size = data_size // channel * channel
        if sample_size != data_size:
            audio = audio[:sample_size]

        #Handles 2 or more channels
        audio = audio.reshape((-1, channel))

        try:
            #Save original shape and reshape the audio to "reduce" its size
            orig_shape = audio.shape
            audio = np.reshape(audio, (2, -1))

            #noise reduction and reshape back to original audio shape
            audio = nr.reduce_noise(audio, rate)
            audio = audio.reshape(orig_shape)
        except:
            #If audio file is too small there is not enough time for the mask smoothing (set it to 60)
            orig_shape = audio.shape
            audio = np.reshape(audio, (2, -1))
            audio = nr.reduce_noise(audio, rate, time_mask_smooth_ms=60)
            audio = audio.reshape(orig_shape)

        numChannels, sampleRate, bitsPerSample, subchunk2Size, _ = playback.getProperties(filePath)
        rawAudio = audio.astype(np.int16).tobytes()

        # Write the WAV file
        with open("noiseReduction.wav", 'wb') as file:
            bytes_rate = rate * numChannels * bitsPerSample
            block_align = numChannels * bitsPerSample / 8
            output = clipping.write2Wave(rawAudio, numChannels, rate, bytes_rate, block_align, bitsPerSample)
            file.write(output)
            file.close()

        # set the player message
        self.__setMessage("Noise removed, select the file to play!")


    def __setMessage(self, string):
        self.message.setText(string)

