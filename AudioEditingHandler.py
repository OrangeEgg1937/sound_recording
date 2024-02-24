# Define the AudioEditingHandler class
import pyaudio
import wave
from PyQt5.QtWidgets import QFileDialog, QMainWindow
from PyQt5.QtCore import Qt
from UI.Ui_mainWindow import Ui_mainWindow
from ImportHandler import ImportHandler
import clipping
import playback
import datetime
import re

# This class is mainly for the Editing page of the application

class AudioEditingHandler:
    fileName = ""
    filePath = ""
    audioEndTime = 0
    audioStartTime = 0
    def __init__(self, p:pyaudio.PyAudio, uiElements:Ui_mainWindow, mainWindow:QMainWindow, importHandler:ImportHandler):
        self.p = p
        self.uiElements = uiElements
        self.mainWindow = mainWindow
        self.importHandler = importHandler

        # Add the listener for the user selected file
        self.uiElements.audioFileList.clicked.connect(self.__fileSelectedByUser)

        # Add the listener for the starting time line edit
        self.uiElements.editStartingTime.editingFinished.connect(self.__startingTimeChanged)

        # Add the listener for the ending time line edit
        self.uiElements.editEndingTime.editingFinished.connect(self.__endingTimeChanged)

        # Add the listener for the starting time slider
        self.uiElements.editStartingTimeSlider.valueChanged.connect(self.__startingTimeSliderChanged)

        # Add the listener for the ending time slider
        self.uiElements.editEndingTimeSlider.valueChanged.connect(self.__endingTimeSliderChanged)

        # Add the listener for the cut and save button
        self.uiElements.cutAndSaveBtn.clicked.connect(self.__cutAndSaveButtonClicked)

        # Add the listener for the overwrite button
        self.uiElements.overwriteBtn.clicked.connect(self.__overwriteButtonClicked)

        # Add the listener for the editRecordBtn button
        self.uiElements.editRecordBtn.clicked.connect(self.__editRecordButtonClicked)

        # Add the listener for the editPauseRecBtn button
        self.uiElements.editPauseRecBtn.clicked.connect(self.__editPauseRecButtonClicked)

        # Add the listener for the editStopRecBtn button
        self.uiElements.editStopRecBtn.clicked.connect(self.__editStopRecButtonClicked)

    # listener for the user selected file
    def __fileSelectedByUser(self):
        # get the selected file name
        self.fileName = self.uiElements.audioFileList.currentItem().text()
        self.filePath = self.importHandler.getCurrentSelectedFile()
        # set the selected file to the selected file line edit
        self.uiElements.editFileName.setText(self.fileName)

        # decode the audio file
        self.audio, self.samples, self.channel = playback.decode_wav(self.fileName)

        # get the audio information
        self.audioEndTime = len(self.audio)/(self.samples*self.channel*1.0)

        # set the starting time slider
        self.uiElements.editStartingTimeSlider.setRange(0, self.audioEndTime)
        self.uiElements.editStartingTimeSlider.setValue(0)

        # set the ending time slider
        self.uiElements.editEndingTimeSlider.setRange(0, self.audioEndTime)
        self.uiElements.editEndingTimeSlider.setValue(self.audioEndTime)

        # set the starting time line edit
        self.uiElements.editStartingTime.setText("00:00:00")

        # set the ending time line edit
        self.uiElements.editEndingTime.setText(self.seconds_to_time(self.audioEndTime))

        # set the duration line edit
        self.uiElements.editDuration.setText(self.seconds_to_time(self.audioEndTime))

    # listener for the starting time line edit
    def __startingTimeChanged(self):
        # checking the input time format
        if not self.is_valid_time_format(self.uiElements.editStartingTime.text()):
            # restore to the previous time
            self.uiElements.editStartingTime.setText(self.seconds_to_time(self.audioStartTime))
            self.uiElements.editingMessage.setText("Invalid time format")
            return
        
        # get the starting time
        startingTime = self.time_to_seconds(self.uiElements.editStartingTime.text())
        # set the starting time slider
        self.uiElements.editStartingTimeSlider.setValue(startingTime)

    # listener for the ending time line edit
    def __endingTimeChanged(self):
        # checking the input time format
        if not self.is_valid_time_format(self.uiElements.editEndingTime.text()):
            # restore to the previous time
            self.uiElements.editEndingTime.setText(self.seconds_to_time(self.audioEndTime))
            self.uiElements.editingMessage.setText("Invalid time format")
            return
        
        # get the starting time
        startingTime = self.time_to_seconds(self.uiElements.editEndingTime.text())
        # set the starting time slider
        self.uiElements.editEndingTimeSlider.setValue(startingTime)
                                           
    # listener for the starting time slider
    def __startingTimeSliderChanged(self):
        # get the starting time
        self.audioStartTime = self.uiElements.editStartingTimeSlider.value()
        # set the starting time line edit
        self.uiElements.editStartingTime.setText(self.seconds_to_time(self.audioStartTime))

    # listener for the ending time slider
    def __endingTimeSliderChanged(self):
        # get the ending time
        self.audioEndTime = self.uiElements.editEndingTimeSlider.value()
        # set the ending time line edit
        self.uiElements.editEndingTime.setText(self.seconds_to_time(self.audioEndTime))

    # listener for the cut and save button
    def __cutAndSaveButtonClicked(self):
        # check the input time is valid or not
        if not self.validTime():
            self.uiElements.editingMessage.setText("Invalid time input")
            return
        # set the editing message and display all varaibles
        self.uiElements.editingMessage.setText(f"In AudioEditingHandler:__cutAndSaveButtonClicked(), st:{self.audioStartTime} et:{self.audioEndTime} path:{self.fileName}")
    
    # listener for the overwrite button
    def __overwriteButtonClicked(self):
        # check the input time is valid or not
        if not self.validTime():
            self.uiElements.editingMessage.setText("Invalid time input")
            return
        # set the editing message and display all varaibles
        self.uiElements.editingMessage.setText(f"In AudioEditingHandler:__overwriteButtonClicked(), st:{self.audioStartTime} et:{self.audioEndTime} path:{self.fileName}")
  
    # listener for the editRecordBtn button
    def __editRecordButtonClicked(self):
        # check the input time is valid or not
        if not self.validTime():
            self.uiElements.editingMessage.setText("Invalid time input")
            return
        # set the player message
        self.uiElements.editingMessage.setText("Recording...")

        # disable the cut and save button and record button
        self.uiElements.cutAndSaveBtn.setEnabled(False)
        self.uiElements.editRecordBtn.setEnabled(False)

        # enable the pause and stop button
        self.uiElements.editPauseRecBtn.setEnabled(True)
        self.uiElements.editStopRecBtn.setEnabled(True)
    
    # listener for the editPauseRecBtn button
    def __editPauseRecButtonClicked(self):
        # set the player message
        self.uiElements.editingMessage.setText("Recording paused")

    # listener for the editStopRecBtn button
    def __editStopRecButtonClicked(self):
        # set the player message
        self.uiElements.editingMessage.setText("Recording stopped")

        # enable the cut and save button and record button
        self.uiElements.cutAndSaveBtn.setEnabled(True)
        self.uiElements.editRecordBtn.setEnabled(True)

        # disable the pause and stop button
        self.uiElements.editPauseRecBtn.setEnabled(False)
        self.uiElements.editStopRecBtn.setEnabled(False)

    # return a string of the time in hh:mm:ss format
    def seconds_to_time(self, seconds) -> str :
        duration = datetime.timedelta(seconds=seconds)

        # calculate the time
        hours = duration.seconds // 3600
        minutes = (duration.seconds % 3600) // 60
        seconds = duration.seconds % 60

        # return the time in hh:mm:ss format
        return f"{hours:02}:{minutes:02}:{seconds:02}"
    
    # check the input time format
    def is_valid_time_format(self, time_str):
        pattern = r'^([0-1][0-9]|2[0-3]):([0-5][0-9]):([0-5][0-9])$'
        match = re.match(pattern, time_str)
        return bool(match)  
    
    # extract the time string to seconds
    def time_to_seconds(self, time_str):
        try:
            time_obj = datetime.datetime.strptime(time_str, "%H:%M:%S")
            total_seconds = time_obj.hour * 3600 + time_obj.minute * 60 + time_obj.second
            return total_seconds
        except ValueError:
            return None
        
    # validate the time is valid or not
    def validTime(self):
        if self.audioStartTime <= self.audioEndTime:
            return True
        else:
            return False
