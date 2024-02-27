# Define the AudioVisualHandler class
import sys, random
from PyQt5.QtWidgets import QMainWindow, QPushButton, QVBoxLayout, QWidget, QScrollArea, QFrame, QApplication, QGridLayout
from PyQt5.QtCore import Qt
from UI.Ui_mainWindow import Ui_mainWindow
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

class MyApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Audio Visual")
        self.setMinimumSize(800, 600)
        
        self.scrollArea = QScrollArea()
        self.scrollArea.setWidgetResizable(True)

        self.layout = QVBoxLayout(self)
        self.setLayout(self.layout)

        # graph window container
        self.graphContainer = QWidget()
        self.gridLayout = QGridLayout(self.graphContainer)

        self.scrollArea.setWidget(self.graphContainer)
        self.layout.addWidget(self.scrollArea)

        self.create_graph()

    def create_graph(self):
        tracker = 0

        for i in range(2):
            for j in range(2):
                tracker += 1

                frame = QFrame()
                frame.setStyleSheet("background-color: white")
                frame.setFrameStyle(QFrame.Panel | QFrame.Raised)

                frameContainer = QVBoxLayout()
                charData = [1,2,3,4,5]

                # create matplotlib graph
                figure = Figure()
                canvas = FigureCanvas(figure)
                ax = figure.add_subplot()
                ax.plot(charData, '-')
                figure.suptitle("Audio Visual")
                canvas.draw()

                frameContainer.addWidget(canvas)

                # box = QVBoxLayout()
                # box.addWidget(frame)

                self.gridLayout.addLayout(frameContainer, i, j)
    

if __name__ == '__main__':
    app = QApplication(sys.argv)

    myApp = MyApp()
    myApp.show()

    try:
        sys.exit(app.exec_())
    except SystemExit:
        print("Closing the application")