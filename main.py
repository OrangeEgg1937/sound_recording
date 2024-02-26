import sys
from PyQt5.QtWidgets import QApplication, QMainWindow

# imort the UI file
from UI.Ui_mainWindow import Ui_mainWindow
from AudioPlayerSettingHandler import AudioPlayerSettingHandler
from ImportHandler import ImportHandler
from PlayerControllerHandler import PlayerControllerHandler
from RecordingHandler import RecordingHandler
from AudioEditingHandler import AudioEditingHandler

# main program
if __name__ == "__main__":
      # initialize all the necessary objects
      app = QApplication(sys.argv) # create the application
      mainWindow = QMainWindow() # create the main window
      ui = Ui_mainWindow() # create the UI object

      # define the ui
      ui.setupUi(mainWindow) # setup the UI

      # define the audio player setting handler
      audioPlayerSettingHandler = AudioPlayerSettingHandler(ui, mainWindow)

      # define the import handler
      importHandler = ImportHandler(ui, mainWindow)

      # define the player controller handler
      playerControllerHandler = PlayerControllerHandler(ui, mainWindow, importHandler)

      # define the recording handler
      recordingHandler = RecordingHandler(ui, mainWindow)

      # define the audio editing handler
      # audioEditingHandler = AudioEditingHandler(ui, mainWindow, importHandler)

      # show the main window
      mainWindow.show()
      sys.exit(app.exec_())
