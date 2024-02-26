import wave
import numpy as np
import matplotlib.pyplot as plt

# Open the .wav file
wav_file = wave.open('sample-file-4.wav', 'rb')

# Get the number of frames, channels, and sample width
num_frames = wav_file.getnframes()
num_channels = wav_file.getnchannels()
sample_width = wav_file.getsampwidth()

# Read the raw audio data
raw_data = wav_file.readframes(num_frames)

# Convert the raw byte data to a NumPy array of integers
audio_data = np.frombuffer(raw_data, dtype=np.int16)

# Close the .wav file
wav_file.close()

# Calculate the duration of the audio
duration = num_frames / float(wav_file.getframerate())

# Create a time axis based on the duration of the audio
time = np.arange(len(audio_data))

# Plot the audio waveform
plt.plot(time, audio_data)
plt.xlabel('Time (s)')
plt.ylabel('Amplitude')
plt.title('Audio Waveform')
plt.grid(True)
plt.show()