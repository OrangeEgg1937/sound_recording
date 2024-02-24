import pyaudio
import wave
import threading

class Audio():
    _num_channel = 1
    _sample_format = pyaudio.paInt16
    _frame_rate = 44100
    _audio = pyaudio.PyAudio()
    _stream = None
    _frames = b''
    _is_recording = False

    @property
    def num_channel(self):
        return self._num_channel

    @property
    def frame_rate(self):
        return self._frame_rate
    
    @property
    def sample_format(self):
        return self._sample_format

    def __init__(self,
                 num_channel: int = 1,
                 smaple_format = pyaudio.paInt16,
                 frame_rate: int = 4410):
        if type(num_channel) is int:
            self._num_channel = max(1, num_channel)
        if type(frame_rate) is int:
            self._frame_rate = max(1, frame_rate)
        if smaple_format in [pyaudio.paInt8, pyaudio.paInt16, pyaudio.paInt24, pyaudio.paInt32]:
            self._sample_format = smaple_format

        self._stream = self._audio.open(
            format=pyaudio.paInt16,
            channels=self.num_channel,
            rate=self.frame_rate,
            input=True,
            output=False,
            start=False,
            frames_per_buffer=512
        )

    def __del__(self):
        if type(self._audio) is pyaudio.PyAudio:
            self._audio.terminate()
        if type(self._stream) is pyaudio.Stream:
            self._stream.close()
        del self._stream

    def start_recording(self):
        self._frames = b''
        threading._start_new_thread(self._start_recording, ())

    def _start_recording(self):
        self._stream.start_stream()
        self._is_recording = True
        while self._is_recording:
            self._frames += self._stream.read(512, exception_on_overflow=False)

    def stop_recording(self):
        self._is_recording = False
        self._stream.stop_stream()
        
    def write(self, filepath: str):
        file = wave.open(filepath, 'wb')
        file.setnchannels(self.num_channel)
        file.setsampwidth(pyaudio.get_sample_size(self._sample_format))
        file.setframerate(self.frame_rate)
        file.writeframes(self._frames)
        file.close()