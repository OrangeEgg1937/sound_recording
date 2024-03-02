from record import Audio
import sounddevice as sd
import time



print("Running")
device_info = sd.query_devices(None, 'input')
audio = Audio()
audio.start_recording(device_info)
time.sleep(5)
audio.stop_recording()
audio.write("test.wav")
print("End")