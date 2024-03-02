# Define the AudioPlayerSettingHandler class
import os
import sounddevice as sd
from PyQt5.QtWidgets import QFileDialog, QMainWindow, QListWidgetItem
from PyQt5.QtCore import Qt
from UI.Ui_mainWindow import Ui_mainWindow

# This class is mainly for the Setting page of the application

class InputDeviceInfo:
    def __init__(self, name:str, index:int):
        self.name = name
        self.index = index

class AudioPlayerSettingHandler:
    def __init__(self, uiElements:Ui_mainWindow, mainWindow:QMainWindow):
        self.uiElements = uiElements
        self.mainWindow = mainWindow
        self.inputDevice = -1
        self.savingPath = os.getcwd()
        self.selectedAudioInputDriver = None

        # Get the available audio devices
        device_info = sd.query_devices()

        # get the dafault input device
        default = device_info[sd.default.device[0]]
        tempd = InputDeviceInfo(default['name'], default['index'])
        self.selectedAudioInputDriver = tempd.index

        # add the default input device to the combo box
        self.uiElements.audioInputDriver.addItem(tempd.name, 0)
        self.uiElements.audioInputDriver.setItemData(0, tempd)

        # Add the available input devices to the combo box
        curr = 1
        for i in range(len(device_info)):
            # if it is a input device add it into the list
            if device_info[i]['max_input_channels'] > 0 and device_info[i]['name'] != default['name']:
                temp = InputDeviceInfo(device_info[i]['name'], device_info[i]['index'])

                # add the item to the combo box
                self.uiElements.audioInputDriver.addItem(temp.name, curr)

                # Set custom data for the item
                self.uiElements.audioInputDriver.setItemData(curr, temp)

                # increment the index
                curr += 1

        # Add the listener for the audio input driver combo box
        self.uiElements.audioInputDriver.currentIndexChanged.connect(self.__audioInputDriverChanged)

        # init the saving path
        self.uiElements.SavingPath.setText(self.savingPath)

        # Add the listener for the save path button
        self.uiElements.SavingPathEdit.clicked.connect(self.__savePathButtonClicked)

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
        return self.selectedAudioInputDriver
    
    # listener for the user selected driver
    def __audioInputDriverChanged(self, i):
        # get the data from the item
        data = self.uiElements.audioInputDriver.itemData(i)
        self.selectedAudioInputDriver = data.index

