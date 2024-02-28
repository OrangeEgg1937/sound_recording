# Define the AudioPlayerSettingHandler class
import os
from PyQt5.QtWidgets import QFileDialog, QMainWindow
from PyQt5.QtCore import Qt
from UI.Ui_mainWindow import Ui_mainWindow
import sounddevice as sd

# This class is mainly for the Setting page of the application

class AudioPlayerSettingHandler:
    def __init__(self, uiElements:Ui_mainWindow, mainWindow:QMainWindow):
        self.uiElements = uiElements
        self.mainWindow = mainWindow
        self.inputDevice = -1
        self.savingPath = os.getcwd()

        # Get the available audio devices
        self.device_info = sd.query_devices(None, 'input')


        print(self.device_info)
        print(self.device_info['name'])

        # Add the available input devices to the combo box
        self.uiElements.audioInputDriver.addItem(self.device_info['name'], self.device_info['index'])

        # Add the listener for the audio input driver combo box
        self.uiElements.audioInputDriver.currentIndexChanged.connect(self.__audioInputDriverChanged)

        # init the saving path
        self.uiElements.SavingPath.setText(self.savingPath)

        # Add the listener for the save path button
        self.uiElements.SavingPathEdit.clicked.connect(self.__savePathButtonClicked)
    
    # listener for the audio input driver combo box
    def __audioInputDriverChanged(self, i):
        # get and set the selected audio input driver index
        self.inputDevice = self.uiElements.audioInputDriver.itemData(i)

    # listener for the save path button
    def __savePathButtonClicked(self):
        # get the saving path
        self.savingPath = QFileDialog.getExistingDirectory(self.mainWindow, "Select Directory", self.savingPath)
        self.uiElements.SavingPath.setText(self.savingPath)

    # get the input device
    def getInputDevice(self):
        return self.inputDevice
    
    # get the saving path
    def getSavingPath(self):
        return self.savingPath
    
    # get the audio input driver
    def getAudioInputDriver(self):
        return self.device_info

