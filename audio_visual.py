import matplotlib.pyplot as plt
import librosa.display
import numpy as np

def visualize_audio(filename, duration=5):
    # Load the audio file
    audio, sr = librosa.load(filename)

    # Calculate the number of frames for the given duration
    frame_duration = duration * sr

    # Calculate the total number of frames
    total_frames = len(audio)

    # Calculate the number of segments
    num_segments = int(np.ceil(total_frames / frame_duration))

    # Create subplots for each segment
    fig, axes = plt.subplots(num_segments, 1, figsize=(10, 5 * num_segments))
    if num_segments == 1:  # If only one segment, axes will not be iterable
        axes = [axes]

    # Iterate over segments and plot the waveform
    for i, ax in enumerate(axes):
        start_frame = i * frame_duration
        end_frame = min((i + 1) * frame_duration, total_frames)
        segment = audio[start_frame:end_frame]

        # Display the waveform
        librosa.display.waveplot(segment, sr=sr, ax=ax)
        ax.set(title=f"Segment {i+1}", xlabel='Time (s)', ylabel='Amplitude')

    # Adjust spacing between subplots
    plt.tight_layout()

    # Show the plot
    plt.show()

# Example usage
filename = "sample-file-4.wav"
visualize_audio(filename, duration=5)