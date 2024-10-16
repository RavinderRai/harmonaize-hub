import os

# Audio generation settings
SAMPLE_RATE = 32000
AUDIO_DURATION = 10  # seconds

# Visualization settings
FPS = 30
FFT_WINDOW_SECONDS = 0.25
FREQ_MIN = 10
FREQ_MAX = 1000
TOP_NOTES = 3
NOTE_NAMES = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
RESOLUTION = (1920, 1080)
SCALE = 2

# File paths
AUDIO_OUTPUT_DIR = 'audio_output'
FRAMES_DIR = os.path.join(AUDIO_OUTPUT_DIR, 'frames')
AUDIO_FILE = os.path.join(AUDIO_OUTPUT_DIR, 'audio_0.wav')
VIDEO_FILE = os.path.join('media', 'movie.mp4')
