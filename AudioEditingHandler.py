# Define the AudioEditingHandler class
from PyQt5.QtWidgets import QFileDialog, QMainWindow
from PyQt5.QtCore import Qt
from UI.Ui_mainWindow import Ui_mainWindow
from ImportHandler import ImportHandler
import playback
import datetime
import re
import os
import clipping
from record import Audio
from PyQt5.QtCore import QTimer

# This class is mainly for the Editing page of the application

class AudioEditingHandler:
    fileName = ""
    filePath = ""
    audioEndTime = 0
    audioStartTime = 0
    recordedAudio = None
    timer = None
    currentRecordedTime = 0
    fileName2 = ""
    filePath2 = ""
    isPaused = False

    def __init__(self, uiElements:Ui_mainWindow, mainWindow:QMainWindow, importHandler:ImportHandler):
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

        # Add the listener for the importCoverFIleBtn button
        self.uiElements.importCoverFIle.clicked.connect(self.__fileSelected)

        self.timer = QTimer()
        self.timer.timeout.connect(self.__updateTime)

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
        self.uiElements.editStartingTimeSlider.setRange(0, int(self.audioEndTime))
        self.uiElements.editStartingTimeSlider.setValue(0)

        # set the ending time slider
        self.uiElements.editEndingTimeSlider.setRange(0, int(self.audioEndTime))
        self.uiElements.editEndingTimeSlider.setValue(int(self.audioEndTime))

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
        self.uiElements.editingMessage.setText(f"Audio is cutted, from:{self.audioStartTime} to:{self.audioEndTime} path:{self.fileName}")
        clipping.trim(self.filePath, self.audioStartTime, self.audioEndTime)

    
    # listener for the overwrite button
    def __overwriteButtonClicked(self):
        # check the input time is valid or not
        if not self.validTime():
            self.uiElements.editingMessage.setText("Invalid time input")
            return

        # check the file is selected or not
        if self.fileName2 == "" or self.filePath2 == "" or self.filePath == "" or self.fileName == "":
            self.uiElements.editingMessage.setText("No file selected")
            return

        # set the editing message and display all varaibles
        self.uiElements.editingMessage.setText("File is overwritten, a new file (overwrite.wav) is created")


        # overwrite the audio file
        clipping.overwrite(self.filePath, self.filePath2, self.audioStartTime)
        
  
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

        # start recording
        self.recordedAudio = Audio()
        self.recordedAudio.start_recording()

        # update the time
        self.uiElements.recordTime.setText("00:00:00")

        # reset the current recorded time
        self.currentRecordedTime = 0

        # start the timer
        self.timer.start(1000)

    
    # listener for the editPauseRecBtn button
    def __editPauseRecButtonClicked(self):
        if self.isPaused:
            self.isPaused = False
            self.uiElements.editingMessage.setText("Resume Recording...")

            # reusme the recording
            self.recordedAudio.start_recording()

            # start the timer
            self.timer.start(1000)
        else:
            self.isPaused = True
            self.uiElements.editingMessage.setText("Recording paused")

            # stop the timer
            self.timer.stop()

            # pause the recording
            self.recordedAudio.pause_recording()

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

        # stop the timer
        self.timer.stop()

        # stop recording
        self.recordedAudio.stop_recording()

        # write the file
        self.recordedAudio.write("temp.wav")

        # set the file2 and path2
        self.fileName2 = "temp.wav"
        self.filePath2 = os.getcwd() + "\\temp.wav"

        print(self.filePath2)

        # set the tips
        self.uiElements.owTips.setText("temp.wav")

        # availabe the overwriteBtn
        self.uiElements.overwriteBtn.setEnabled(True)

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
        
    # Refresh the audio file list and current selected file
    def refresh(self):
        self.uiElements.audioFileList.clear()
        self.importHandler.refreshAudioFileList()
        self.uiElements.editFileName.setText(self.importHandler.getCurrentSelectedFile())

    # update the time
    def __updateTime(self):
        self.currentRecordedTime += 1
        duration = datetime.timedelta(seconds=self.currentRecordedTime)

        # calculate the time
        hours = duration.seconds // 3600
        minutes = (duration.seconds % 3600) // 60
        seconds = duration.seconds % 60

        # set the time
        self.uiElements.editRecordTime.setText(f"{hours:02}:{minutes:02}:{seconds:02}")

    def __fileSelected(self):
        # get the file path
        self.filePath2 = QFileDialog.getOpenFileName(self.mainWindow, "Select File", os.getcwd(), "Audio Files (*.wav)")[0]
        self.fileName2 = os.path.basename(self.filePath2)
        if(self.fileName2 != ""):
            # set the tips
            self.uiElements.owTips.setText(self.fileName2)

            # availabe the overwriteBtn
            self.uiElements.overwriteBtn.setEnabled(True)