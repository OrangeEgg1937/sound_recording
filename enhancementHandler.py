# unless specifying a different file, this class will handle the enhancement
import clipping

from PyQt5.QtWidgets import QFileDialog, QMainWindow
from PyQt5.QtCore import Qt
from UI.Ui_mainWindow import Ui_mainWindow
from ImportHandler import ImportHandler
from PyQt5.QtCore import QTimer


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
        if filePath == "":
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

        # check the file path exist or not
        if filePath == "":
            self.__setMessage("Please select a file first!")
            return

        # remove the noise from the file


        # set the player message
        self.__setMessage("Noise removed, select the file to play!")
        


    def __setMessage(self, string):
        self.message.setText(string)

