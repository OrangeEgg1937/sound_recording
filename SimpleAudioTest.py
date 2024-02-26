from record import Audio
import time

audio = Audio()
audio.start_recording()
time.sleep(5)
audio.stop_recording()
audio.write("test.wav")