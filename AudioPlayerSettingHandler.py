# Define the AudioPlayerSettingHandler class
import os
from PyQt5.QtWidgets import QFileDialog, QMainWindow
from PyQt5.QtCore import Qt
from UI.Ui_mainWindow import Ui_mainWindow

# This class is mainly for the Setting page of the application

class AudioPlayerSettingHandler:
    def __init__(self, uiElements:Ui_mainWindow, mainWindow:QMainWindow):
        self.uiElements = uiElements
        self.mainWindow = mainWindow
        self.inputDevice = -1
        self.savingPath = os.getcwd()

        # Get the available audio devices
        # deviceCount = self.p.get_device_count()

        # # Add the available audio devices to the combo box
        # for i in range(deviceCount):
        #     deviceInfo = self.p.get_device_info_by_index(i)
        #     if deviceInfo.get('maxInputChannels') > 0 and deviceInfo["hostApi"] == 1:
        #         # set the combo box item
        #         self.uiElements.audioInputDriver.addItem(deviceInfo["name"])
        #         self.uiElements.audioInputDriver.setItemData(self.uiElements.audioInputDriver.count()-1, i, role=Qt.UserRole)

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

