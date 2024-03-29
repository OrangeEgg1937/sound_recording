import sys
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtCore import Qt

# imort the UI file
from UI.Ui_mainWindow import Ui_mainWindow
from AudioPlayerSettingHandler import AudioPlayerSettingHandler
from ImportHandler import ImportHandler
from PlayerControllerHandler import PlayerControllerHandler
from RecordingHandler import RecordingHandler
from AudioEditingHandler import AudioEditingHandler
from AudioVisualHandler import AudioVisualHandler
from enhancementHandler import EnhancementHandler

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

      # define the audio visual handler
      mainAudioVisualHandler = AudioVisualHandler(ui, mainWindow, importHandler, ui.mainAudioVisual)

      # define the player controller handler
      playerControllerHandler = PlayerControllerHandler(ui, mainWindow, importHandler, mainAudioVisualHandler)

      # define the recording handler
      recordingHandler = RecordingHandler(ui, mainWindow, audioPlayerSettingHandler, importHandler)

      # define the audio editing handler
      audioEditingHandler = AudioEditingHandler(ui, mainWindow, importHandler)

      # define the enhancement handler
      enhancementHandler = EnhancementHandler(ui, mainWindow, importHandler)

      # show the main window
      mainWindow.show()
      sys.exit(app.exec_())
