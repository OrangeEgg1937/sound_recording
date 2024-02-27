# Define the AudioVisualHandler class
import sys, random, playback
import numpy as np
from PyQt5.QtWidgets import QMainWindow, QPushButton, QVBoxLayout, QWidget, QScrollArea, QFrame
from PyQt5.QtCore import Qt
from UI.Ui_mainWindow import Ui_mainWindow
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from ImportHandler import ImportHandler

# This class is mainly for showing the audio and visual data of the player
class AudioVisualHandler:
    def __init__(self, ui:Ui_mainWindow, mainWindow:QMainWindow, importHandler:ImportHandler ,waveContainer:QWidget = None):
        self.uiElements = ui
        self.mainWindow = mainWindow
        self.importHandler = importHandler
        self.waveContainer = waveContainer

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
        figure = Figure()
        canvas = FigureCanvas(figure)
        ax = figure.add_subplot()
        ax.plot(charData, '-')
        figure.suptitle("Audio Visual")
        canvas.draw()

        self.layout.addWidget(canvas)

    def createGraphsFromWAV(self, path):
        # decode the wav file
        audio_data, sample_rate, amount_of_channels = playback.decode_wav(path)

        # calculate the duration
        duration = playback.getDuration(path)

        # calculate the time axis for the graph
        time = np.linspace(0, duration, len(audio_data) // amount_of_channels)

        # Reshape the audio data to match the number of channels
        reshaped_audio_data = np.reshape(audio_data, (-1, amount_of_channels))

        # create matplotlib graph
        figure = Figure()
        canvas = FigureCanvas(figure)
        ax = figure.add_subplot()
        ax.plot(time, reshaped_audio_data)
        figure.suptitle("Audio Visual")
        canvas.draw()

        self.layout.addWidget(canvas)

    def __itemPressed(self):
        # clear all the previous graphs
        for i in reversed(range(self.layout.count())):
            self.layout.itemAt(i).widget().setParent(None)

        # get the data from the item
        filePath = self.importHandler.getCurrentSelectedFile()

        # create the graph
        self.createGraphsFromWAV(filePath)

