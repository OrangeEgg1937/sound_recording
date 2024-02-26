# Define the PlayerControlHandler class
import enum
import pyaudio
import playback
import datetime

from PyQt5.QtWidgets import QMainWindow
from PyQt5.QtCore import QTimer
from UI.Ui_mainWindow import Ui_mainWindow
from ImportHandler import ImportHandler

# Player status
class PlayerStatus(enum.Enum):
    STOP = 0
    PLAYING = 1
    PAUSE = 2

# This class is mainly for the audio player of the application
class PlayerControllerHandler:
    status = PlayerStatus.STOP
    importHandler:ImportHandler = None

    # variable for the audio player
    speed = 1.0
    audio = None
    samples = None
    channel = None
    audioCurrTime = 0   # the current time of the audio (in seconds)
    startTime = 0       # not used
    audioEndTime = 0    # the end time of the audio
    timer = None
    filePath = ""       # the current selected file path of the audio

    def __init__(self, p:pyaudio.PyAudio, uiElements:Ui_mainWindow, mainWindow:QMainWindow, importHandler:ImportHandler):
        self.p = p
        self.uiElements = uiElements
        self.mainWindow = mainWindow
        self.importHandler = importHandler

        # Add the listener for the play button
        self.uiElements.playBtn.clicked.connect(self.__playButtonClicked)

        # Add the listener for the stop button
        self.uiElements.stopBtn.clicked.connect(self.__stopButtonClicked)

        # Add the listener for the pause button
        self.uiElements.pauseBtn.clicked.connect(self.__pauseButtonClicked)

        # Add the listener for the speed control
        self.uiElements.speedControl.currentIndexChanged.connect(self.__speedControlChanged)

        # # Add the listener for the seekbar/slider
        self.uiElements.audioProgBar.sliderMoved.connect(self.__sliderReleased)
        self.uiElements.audioProgBar.sliderReleased.connect(self.__sliderReleased)
        # self.uiElements.audioProgBar.sliderPressed.connect(self.__sliderReleased)
        # self.uiElements.audioProgBar.valueChanged.connect(self.__sliderReleased)

        # Add the listener when the user select a new file
        self.uiElements.audioFileList.itemPressed.connect(self.setPlayerInfo)

        # initialize the timer object
        self.timer = QTimer()

        # set the listener for the timer when count to 
        self.timer.timeout.connect(self.__updateSlider) # the audioProgBar value is incremented by 1 when the timer is triggered

    def __playButtonClicked(self):        
        # if the audio file is playing or invalid file path, return
        if self.importHandler.getCurrentSelectedFile() == None or self.status == PlayerStatus.PLAYING or self.filePath == "":
            return
        
        # play the audio
        self.__audioPlay()

    
    # Playing the audio
    def __audioPlay(self):
        # set the status to playing
        self.status = PlayerStatus.PLAYING
        
        # set the player message:
        self.uiElements.playerMessage.setText("Playing the audio file: " + self.importHandler.getCurrentSelectedFile())

        # play the audio
        playback.play_audio(self.speed, self.audio, self.samples, self.channel, self.audioCurrTime)

        # set the time of the audio to display
        self.uiElements.currentTime.setText(self.seconds_to_time(self.audioCurrTime))
        self.uiElements.endTime.setText(self.seconds_to_time(self.audioEndTime))

        # start counting the playing time
        # 1000ms/speed is the interval of the timer.
        # e.g: 1.0x speed = 1000ms = 1s, 2.0x speed = 500ms = 0.5s, 0.5x speed = 2000ms = 2s
        self.timer.start(1000/self.speed)

    # Update the slider and the current time by one step
    def __updateSlider(self):
        self.uiElements.audioProgBar.setValue(self.uiElements.audioProgBar.value() + 1)
        self.audioCurrTime = self.uiElements.audioProgBar.value()
        self.uiElements.currentTime.setText(self.seconds_to_time(self.uiElements.audioProgBar.value()))
        # check if the audio is finished
        if self.uiElements.audioProgBar.value() >= int(self.audioEndTime):
            self.status = PlayerStatus.STOP
            self.resetPlayer()
            self.uiElements.playerMessage.setText("Audio Ended")
            playback.sd.stop()
            self.timer.stop()

    def __stopButtonClicked(self):
        # stop the audio
        self.uiElements.playerMessage.setText("Audio player stopped")
        self.resetPlayer()

    def __pauseButtonClicked(self):
        if self.status == PlayerStatus.PAUSE or self.status == PlayerStatus.STOP:
            return
        # set the status to pause
        self.status = PlayerStatus.PAUSE
        # stop the audio
        self.uiElements.playerMessage.setText("Audio player paused")
        playback.sd.stop()

        # stop the timer
        self.timer.stop()
    
    def __speedControlChanged(self, i):
        # get the selected speed
        # e.g: 1.0x, 1.5x, 2.0x, 0.5x, since all the speed is in the format of x,
        # we can remove the last character and convert it to float
        self.speed = float(self.uiElements.speedControl.currentText()[:-1]) 

        # set the message
        self.uiElements.playerMessage.setText("Speed changed to " + self.uiElements.speedControl.currentText())
    
    # Assume when the user released the slider, stop the current audio first, play the audio from the new position
    def __sliderReleased(self):
        # stop the audio
        playback.sd.stop()

        # stop the timer
        self.timer.stop()

        # set the current status to pause if it is playing
        if self.status == PlayerStatus.PLAYING:
            self.status = PlayerStatus.PAUSE
        
        self.audioCurrTime = self.uiElements.audioProgBar.value()
        self.uiElements.currentTime.setText(self.seconds_to_time(self.audioCurrTime))
        self.uiElements.playerMessage.setText("Moved slider:" + self.seconds_to_time(self.audioCurrTime) + "s"  + "Current status: " + str(self.status))
        
        # resume the audio
        # if self.status == PlayerStatus.PAUSE:
        #     self.__playButtonClicked() # play the audio from the new position
    
    # Reset the starting time of the player
    def resetPlayer(self):
        self.audioCurrTime = 0
        self.uiElements.audioProgBar.setValue(0)
        self.uiElements.currentTime.setText("00:00:00")
        self.uiElements.endTime.setText(self.seconds_to_time(self.audioEndTime))
        self.status = PlayerStatus.STOP
        playback.sd.stop()
        self.timer.stop()

    # return a string of the time in hh:mm:ss format
    def seconds_to_time(self, seconds) -> str :
        duration = datetime.timedelta(seconds=seconds)

        # calculate the time
        hours = duration.seconds // 3600
        minutes = (duration.seconds % 3600) // 60
        seconds = duration.seconds % 60

        # return the time in hh:mm:ss format
        return f"{hours:02}:{minutes:02}:{seconds:02}"
    
    # set pthe player information when user select a new file
    def setPlayerInfo(self):
        # stop and reset the current audio
        self.resetPlayer()

        # get the file path
        self.filePath = self.importHandler.getCurrentSelectedFile()

        # decode the audio file
        self.audio, self.samples, self.channel = playback.decode_wav(self.filePath)

        # get the audio information
        self.audioEndTime = len(self.audio)/(self.samples*self.channel*1.0)

        # set the time information into the audio
        self.uiElements.audioProgBar.setMaximum(int(self.audioEndTime))
        self.uiElements.audioProgBar.setValue(0)
        self.uiElements.currentTime.setText("00:00:00")
        self.uiElements.endTime.setText(self.seconds_to_time(self.audioEndTime))

        # set the player message
        self.uiElements.playerMessage.setText("File selected, ready to play!")

