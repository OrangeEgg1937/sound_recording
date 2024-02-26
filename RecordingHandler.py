# Define the RecordingHandler class
import enum
import datetime

from UI.Ui_mainWindow import Ui_mainWindow
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtCore import QTimer
from record import Audio

CHANNELS = 2
RATE = 44100
CHUNK = 1024
RECORD_SECONDS = 5

# Recording status
class Recording(enum.Enum):
    STOP = 0
    PLAYING = 1
    PAUSE = 2

# This class is mainly for the recording part of the application
class RecordingHandler:
    timer = None
    recordingFile = None
    currentRecordedTime = 0.0
    stream = None
    audio = None

    # for debug only
    frames = []

    def __init__(self, uiElements:Ui_mainWindow, mainWindow:QMainWindow):
        self.uiElements = uiElements
        self.mainWindow = mainWindow

        # Add the listener for the record button
        self.uiElements.recordBtn.clicked.connect(self.__recordButtonClicked)

        # Add the listener for the stop record button
        self.uiElements.saveRecBtn.clicked.connect(self.__stopRecordButtonClicked)

        # Add the listener for pause record button
        self.uiElements.pauseRecBtn.clicked.connect(self.__pauseRecordButtonClicked)

        self.timer = QTimer()
        self.timer.timeout.connect(self.__updateTime)

    # listener for the record button
    def __recordButtonClicked(self):
        self.uiElements.playerMessage.setText("Recording...")
        self.recording = True

        # start recording
        self.audio = Audio()
        self.audio.start_recording()

        # disable the record button
        self.uiElements.recordBtn.setEnabled(False)

        # enable the stop and pause record button
        self.uiElements.saveRecBtn.setEnabled(True)
        self.uiElements.pauseRecBtn.setEnabled(True)

        # start the timer
        self.timer.start(1000)


    # listener for the stop record button
    def __stopRecordButtonClicked(self):
        self.uiElements.playerMessage.setText("Recording stopped")

        # stop the timer
        self.timer.stop()

        # stop recording
        self.audio.stop_recording()

        # get the current time
        currentTime = datetime.datetime.now()
        formatted_datetime = currentTime.strftime("%d%m%y%H%M%S")

        # write the file
        self.audio.write(f"recording_{formatted_datetime}.wav")

        # enable the record button
        self.uiElements.recordBtn.setEnabled(True)

        # disable the stop and pause record button
        self.uiElements.saveRecBtn.setEnabled(False)
        self.uiElements.pauseRecBtn.setEnabled(False)

        self.audio.__del__()
        self.audio = None

        # reset the current recorded time
        self.currentRecordedTime = 0

        # update the time
        self.uiElements.recordTime.setText("00:00:00")
    
    # listener for the pause record button
    def __pauseRecordButtonClicked(self):
        self.uiElements.playerMessage.setText("Recording paused")

        # stop the timer
        self.timer.stop()

    
    # update the time
    def __updateTime(self):
        self.currentRecordedTime += 1
        duration = datetime.timedelta(seconds=self.currentRecordedTime)

        # calculate the time
        hours = duration.seconds // 3600
        minutes = (duration.seconds % 3600) // 60
        seconds = duration.seconds % 60

        # set the time
        self.uiElements.recordTime.setText(f"{hours:02}:{minutes:02}:{seconds:02}")
    