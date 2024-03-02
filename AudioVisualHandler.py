# Define the AudioVisualHandler class
import playback
import numpy as np
import datetime
import time
import threading
from PyQt5.QtWidgets import QMainWindow, QVBoxLayout, QWidget, QScrollArea
from UI.Ui_mainWindow import Ui_mainWindow
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.patches import Rectangle
from ImportHandler import ImportHandler

# This class is mainly for showing the audio and visual data of the player
class AudioVisualHandler:
    def __init__(self, ui:Ui_mainWindow, mainWindow:QMainWindow, importHandler:ImportHandler ,waveContainer:QWidget = None):
        self.uiElements = ui
        self.mainWindow = mainWindow
        self.importHandler = importHandler
        self.waveContainer = waveContainer
        self.ax = None
        self.canvas = None
        self.figure = None
        self.processRectangle = None
        self.userSelectedLine = None

        # reset the style of the wave container
        self.waveContainer.setStyleSheet("")

        # create a layout for the wave container
        self.layout = QVBoxLayout(self.waveContainer)
        self.area = QScrollArea()
        self.area.setWidgetResizable(True)

        # add the listener for the file list
        self.uiElements.audioFileList.itemPressed.connect(self.__itemPressed)

        self.createEmptyGraph()
    
    def createEmptyGraph(self):
        charData = [0]

        # create matplotlib graph
        figure = Figure(facecolor="#F9F9F9")
        canvas = FigureCanvas(figure)
        ax = figure.add_subplot()
        ax.plot(charData, '-')
        figure.suptitle("Audio Visual will display here, you can select a file from the list first.")
        ax.axis('off')
        canvas.draw()

        self.layout.addWidget(canvas)

    def createGraphsFromWAV(self, path):
        # decode the wav file
        audio_data, sample_rate, amount_of_channels = playback.decode_wav(path)

        # calculate the duration (correct to 2 decimal places)
        duration = round(playback.getDuration(path), 2)

        # Reshape the audio data to match the number of channels
        # if the audio data is stereo, then the audio data will be reshaped to 2 columns
        if amount_of_channels == 1:
            reshaped_audio_data = audio_data
        else:
            # checking the number of sample in raw audio data
            # if the number of sample is odd, then padding a zero to the last sample
            # otherwise, the reshaping process will fail
            padding = len(audio_data) % amount_of_channels
            if padding != 0:
                for i in range(padding):
                    # append a zero to the last sample
                    audio_data = np.append(audio_data, [0])

            # reshape the audio data   
            reshaped_audio_data = np.reshape(audio_data, (-1, amount_of_channels))

            # taking the average of the audio data for each channel (as we only want one channel for the graph)
            reshaped_audio_data = np.mean(reshaped_audio_data, axis=1)
        
        # calculate the time axis for the graph
        time = np.linspace(0, duration, len(reshaped_audio_data))

        # create matplotlib graph
        self.figure = Figure(facecolor="#F9F9F9")
        self.canvas = FigureCanvas(self.figure)

        # plot the graph
        self.ax = self.figure.add_subplot()
        self.ax.plot(time, reshaped_audio_data)

        # register the click event
        self.canvas.mpl_connect('button_press_event', self.__graphClicked)

        # register the hover event
        self.canvas.mpl_connect('motion_notify_event', self.__graphHovered)

        # set the style of the graph
        # Only show the bottom spine
        self.ax.spines['right'].set_visible(False)
        self.ax.spines['top'].set_visible(False)
        self.ax.spines['bottom'].set_visible(True)
        self.ax.spines['left'].set_visible(False)
        self.ax.yaxis.set_ticks_position('none')
        self.ax.xaxis.set_ticks_position('none')

        self.ax.set_yticklabels([]) # remove the y-axis label
        self.ax.set_facecolor("#F9F9F9") # set the background color of the graph
        self.ax.set_xlim(0, duration) # set the x-axis always start from 0
        self.ax.set_xticks(np.arange(0, duration, 1)) # set the x-interval to be 1

        # add it to the GUI
        self.canvas.draw()
        self.layout.addWidget(self.canvas)

    # when user click in the graph, give a response
    def __graphClicked(self, event):
        # if the value is none, then return
        if event.xdata == None:
            return
        
        # get the player slider maximum value
        maxSliderValue = self.uiElements.audioProgBar.maximum()

        # convert the x position to seconds in 2 decimal places
        selectedTime = round(event.xdata, 2)

        # convert the time into slider value and set the slider value
        self.uiElements.audioProgBar.setValue(int(selectedTime * 100))

        # set the current time label with 2 decimal places
        self.uiElements.currentTime.setText(self.second_to_time(selectedTime))

    
    # when user mouse hover in the graph, give a response
    def __graphHovered(self, event):
        # if the value is none, then return
        if event.xdata == None:
            return

        # if the line is  None, then create a new line
        if self.userSelectedLine == None:
            self.userSelectedLine = self.ax.axvline(event.xdata, color="red", linestyle="-")

        # disconnect the hover event first
        self.canvas.mpl_disconnect(self.canvas.mpl_connect('motion_notify_event', self.__graphHovered))

        # set the x position of the line
        self.userSelectedLine.set_xdata(event.xdata)

        # Redraw the graph
        self.canvas.draw()

        # Show the time in the label
        self.uiElements.hoverSecond.setText(self.second_to_time(event.xdata))

        # reconnect the hover event
        self.canvas.mpl_connect('motion_notify_event', self.__graphHovered)

    def __itemPressed(self):
        # clear all the previous graphs
        for i in reversed(range(self.layout.count())):
            self.layout.itemAt(i).widget().setParent(None)
        
        # delete the previous object
        self.ax = None
        self.canvas = None
        self.figure = None
        self.processRectangle = None
        self.userSelectedLine = None

        # get the data from the item
        filePath = self.importHandler.getCurrentSelectedFile()

        # create the graph
        self.createGraphsFromWAV(filePath)

        # set the song title
        songTitle = self.importHandler.currentSelectedFile.name
        songTitle = songTitle.split(".")[0] # remove the .wav or .mp3 from the song title
        self.uiElements.AudioTitle.setText(songTitle)

    # disable the click and hover event
    def disableGraphEvent(self):
        # check if the canvas is not none
        if self.canvas == None:
            return
        self.canvas.mpl_disconnect(self.canvas.mpl_connect('button_press_event', self.__graphClicked))
        self.canvas.mpl_disconnect(self.canvas.mpl_connect('motion_notify_event', self.__graphHovered))
    
    # enable the click and hover event
    def enableGraphEvent(self):
        # check if the canvas is not none
        if self.canvas == None:
            return
        self.canvas.mpl_connect('button_press_event', self.__graphClicked)
        self.canvas.mpl_connect('motion_notify_event', self.__graphHovered)

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
        
