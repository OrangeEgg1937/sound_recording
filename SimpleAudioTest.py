import pyaudio
import wave

chunk = 1024  # Number of frames in each buffer
sample_format = pyaudio.paInt16  # 16 bits per sample
channels = 1  # Mono audio
sample_rate = 44100  # Common sample rate for audio

# Initialize PyAudio
p = pyaudio.PyAudio()

# dispaly the available audio devices
for i in range(p.get_device_count()):
    # check if the device is an input device
    if p.get_device_info_by_index(i).get('maxInputChannels') > 0 and p.get_device_info_by_index(i)["hostApi"] == 0:
        print(f"Input Device {i}: {p.get_device_info_by_index(i)}")

# Open the microphone input stream
stream = p.open(input_device_index=0,
                format=sample_format,
                channels=channels,
                rate=sample_rate,
                frames_per_buffer=chunk,
                input=True)

print("Recording...")

frames = []  # List to store audio frames

# Capture audio data in chunks and append to the frames list
while True:
    data = stream.read(chunk)
    frames.append(data)

# Stop and close the stream
stream.stop_stream()
stream.close()

# Terminate the PyAudio instance
p.terminate()

print("Recording finished.")

# Save the audio data as a WAV file
wf = wave.open("output.wav", "wb")
wf.setnchannels(channels)
wf.setsampwidth(p.get_sample_size(sample_format))
wf.setframerate(sample_rate)
wf.writeframes(b''.join(frames))
wf.close()