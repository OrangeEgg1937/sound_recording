# Define the AudioPlayerSettingHandler class
import pyaudio
import os
from PyQt5.QtWidgets import QFileDialog, QMainWindow, QListWidget, QListWidgetItem, QWidget
from PyQt5.QtCore import Qt
from UI.Ui_mainWindow import Ui_mainWindow

# This class is mainly for the import (The left most part) of the application

# define a class for saving the file path and the file name
class ImportedFile:
    def __init__(self, path:str, name:str):
        self.path = path
        self.name = name

class ImportHandler:
    currentSelectedFile = None

    def __init__(self, p:pyaudio.PyAudio, uiElements:Ui_mainWindow, mainWindow:QMainWindow):
        self.p = p
        self.uiElements = uiElements
        self.mainWindow = mainWindow
        self.inputDevice = -1
        self.savingPath = os.getcwd()

        # add the listener for the file select button
        self.uiElements.importFileBtn.clicked.connect(self.__fileSelected)

        # add the listener for the file list
        self.uiElements.audioFileList.itemPressed.connect(self.__itemPressed)

        # add the listener for the remove file button
        self.uiElements.removeSelectedBtn.clicked.connect(self.__removeFile)

    # listener for the user selected file
    def __fileSelected(self):
        # get the file path
        filePath = QFileDialog.getOpenFileName(self.mainWindow, "Select File", os.getcwd(), "Audio Files (*.wav *.mp3)")[0]
        fileName = os.path.basename(filePath)
        temp = ImportedFile(filePath, fileName)

        # Create QListWidgetItem and set the name
        item = QListWidgetItem(fileName)

        # set the data for the item
        item.setData(Qt.UserRole, temp)

        # add the file to the list
        self.uiElements.audioFileList.addItem(item)

        # set the player message
        self.uiElements.playerMessage.setText("File imported, select the file to play!")
    
    # listener for the user selected file
    def __itemPressed(self, item:QListWidgetItem):
        # get the data from the item
        data = item.data(Qt.UserRole)
        self.currentSelectedFile = data
        
        # set the selected file text
        self.uiElements.selectedFileName.setText(self.currentSelectedFile.name)

    # listener for the remove file button
    def __removeFile(self):
        # remove the selected file
        self.uiElements.audioFileList.takeItem(self.uiElements.audioFileList.currentRow())
        self.currentSelectedFile = None
        self.uiElements.selectedFileName.setText("")

        # set the player message
        self.uiElements.playerMessage.setText("File removed, select another file to play!")

    # return the current selected file path
    def getCurrentSelectedFile(self):
        if self.currentSelectedFile == None:
            return None
        return self.currentSelectedFile.path
    
    