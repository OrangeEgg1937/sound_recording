# Define the PlayerControlHandler class
import enum
import playback
import datetime
import math
import record

from PyQt5.QtWidgets import QMainWindow
from PyQt5.QtCore import QTimer
from UI.Ui_mainWindow import Ui_mainWindow
from ImportHandler import ImportHandler
from AudioVisualHandler import AudioVisualHandler

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
    audioCurrTime = 0.00   # the current time of the audio (in s)
    startTime = 0       # not used
    audioEndTime = 0.00    # the end time of the audio (in s)
    timer = None
    filePath = ""       # the current selected file path of the audio

    def __init__(self, uiElements:Ui_mainWindow, mainWindow:QMainWindow, importHandler:ImportHandler, audioVisualHandler:AudioVisualHandler):
        self.uiElements = uiElements
        self.mainWindow = mainWindow
        self.importHandler = importHandler
        self.audioVisualHandler = audioVisualHandler

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
        self.timer.timeout.connect(self.__updateWhenTimeout) # the audioProgBar value is incremented by 1 when the timer is triggered

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

        # get the current time of the audio
        self.audioCurrTime = self.uiElements.audioProgBar.value()/100.0

        # set the time of the audio to display
        self.uiElements.currentTime.setText(self.second_to_time(self.audioCurrTime))
        self.uiElements.endTime.setText(self.second_to_timeNoMs(self.audioEndTime))

        # start counting the playing time
        # we would like to update the slider every 0.01 second (10ms)
        # 1.0x speed: update it every 10ms, 1.5x speed: update it every 6.67ms, 
        # 2.0x speed: update it every 5ms, 0.5x speed: update it every 20ms
        # which is 1000/speed
        self.timer.start(int(10/self.speed))

        # disable the graph event
        self.audioVisualHandler.disableGraphEvent()

    # Update the slider and the current time by one step
    def __updateWhenTimeout(self):
        self.uiElements.audioProgBar.setValue(self.uiElements.audioProgBar.value() + 1)
        self.audioCurrTime = self.sliderValueToSeconds(self.uiElements.audioProgBar.value())
        self.uiElements.currentTime.setText(self.second_to_time(self.audioCurrTime))
        # check if the audio is finished
        if self.audioCurrTime >= (self.audioEndTime - 0.01):
            self.status = PlayerStatus.STOP
            self.resetPlayer()
            self.uiElements.playerMessage.setText("Audio Ended")
            playback.sd.stop()
            self.timer.stop()

    def __stopButtonClicked(self):
        # stop the audio
        self.uiElements.playerMessage.setText("Audio player stopped")
        self.resetPlayer()

        # enable the graph event
        self.audioVisualHandler.enableGraphEvent()

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

        # enable the graph event
        self.audioVisualHandler.enableGraphEvent()
    
    def __speedControlChanged(self, i):
        # get the selected speed
        # e.g: 1.0x, 1.5x, 2.0x, 0.5x, since all the speed is in the format of x,
        # we can remove the last character and convert it to float
        self.speed = float(self.uiElements.speedControl.currentText()[:-1])

        # stop the current audio
        playback.sd.stop()

        # stop the timer
        self.timer.stop()

        # set the message
        self.uiElements.playerMessage.setText("Speed changed to " + self.uiElements.speedControl.currentText())

        # if the audio is playing, play the audio again
        if self.status == PlayerStatus.PLAYING:
            self.__audioPlay()
    
    # Assume when the user released the slider, stop the current audio first, play the audio from the new position
    def __sliderReleased(self):
        # stop the audio
        playback.sd.stop()

        # stop the timer
        self.timer.stop()

        # set the current status to pause if it is playing
        if self.status == PlayerStatus.PLAYING:
            self.status = PlayerStatus.PAUSE
        
        self.audioCurrTime = self.sliderValueToSeconds(self.uiElements.audioProgBar.value())
        self.uiElements.currentTime.setText(self.second_to_time(self.audioCurrTime))
        self.uiElements.playerMessage.setText("Moved slider:" + str(self.audioCurrTime) + "s"  + "Current status: " + str(self.status))
        
        # resume the audio
        # if self.status == PlayerStatus.PAUSE:
        #     self.__playButtonClicked() # play the audio from the new position
    
    # Reset the starting time of the player
    def resetPlayer(self):
        self.audioCurrTime = 0
        self.uiElements.audioProgBar.setValue(0)
        self.uiElements.currentTime.setText("00:00:00.00")
        self.uiElements.endTime.setText(self.second_to_timeNoMs(self.audioEndTime))
        self.status = PlayerStatus.STOP
        playback.sd.stop()
        self.timer.stop()

    # return a string of the time in hh:mm:ss.ms format
    def second_to_time(self, s) -> str :
        duration = datetime.timedelta(seconds=s)

        # calculate the time
        hours = duration.seconds // 3600
        minutes = (duration.seconds % 3600) // 60
        seconds = duration.seconds % 60
        microseconds = duration.microseconds // 10000

        # return the time in hh:mm:ss:mm format
        return f"{hours:02}:{minutes:02}:{seconds:02}.{microseconds:02}"
    
    # return a string of the time in hh:mm:ss.ms format
    def second_to_timeNoMs(self, s) -> str :
        duration = datetime.timedelta(seconds=s)

        # calculate the time
        hours = duration.seconds // 3600
        minutes = (duration.seconds % 3600) // 60
        seconds = duration.seconds % 60

        # return the time in hh:mm:ss:mm format
        return f"{hours:02}:{minutes:02}:{seconds:02}"

    # convert the slider value to time
    def sliderValueToTime(self, value) -> str:
        return self.second_to_time(value/100.0)
    
    # convert the slider value to seconds in float
    def sliderValueToSeconds(self, value) -> float:
        return value/100.0
    
    # set pthe player information when user select a new file
    def setPlayerInfo(self):
        # stop and reset the current audio
        self.resetPlayer()

        # get the file path
        self.filePath = self.importHandler.getCurrentSelectedFile()

        # decode the audio file
        self.audio, self.samples, self.channel = playback.decode_wav(self.filePath)

        # decode the file with raw byte and get the text
        raw_data, _, _ = playback.decode2Raw(self.filePath)
        
        # set the speech to text
        try:
            self.uiElements.speech2text.setText(record.speech_to_text(raw_data, self.samples))
        except:
            self.uiElements.speech2text.setText("The audio is not supported for speech to text conversion. Please try another audio file.") 

        # get the audio information
        self.audioEndTime = math.ceil(len(self.audio)/(self.samples*self.channel*1.0)) # in s

        # set the time information into the audio
        # since the audioProgBar support to 0.01s, we need to multiply the audioEndTime by 100
        self.uiElements.audioProgBar.setMaximum((self.audioEndTime)*100)
        self.uiElements.audioProgBar.setValue(0)
        self.uiElements.currentTime.setText("00:00:00.00")
        self.uiElements.endTime.setText(self.second_to_timeNoMs(self.audioEndTime))

        # print out the duration of the audio
        print("Duration of the audio: " + str(playback.getDuration(self.filePath)) + "s")

        # set the player message
        self.uiElements.playerMessage.setText("File selected, ready to play!")

