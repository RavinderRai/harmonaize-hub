import os
import numpy as np
import logging
import matplotlib.pyplot as plt
from scipy.io import wavfile
import plotly.graph_objects as go
import shutil
import subprocess
from tqdm import tqdm
from .utils import note_name, freq_to_number
from .config import (
    AUDIO_FILE,
    FFT_WINDOW_SECONDS,
    TOP_NOTES,
    FRAMES_DIR,
    SCALE,
    FPS,
    VIDEO_FILE,
    FREQ_MIN,
    FREQ_MAX,
    RESOLUTION
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def plot_fft(p: np.ndarray, xf: np.ndarray, fs: int, notes: list, dimensions: tuple = (960, 540)) -> go.Figure:
    """
    Plots the FFT (Fast Fourier Transform) results using Plotly.

    Parameters:
    p (np.ndarray): The FFT result array containing magnitudes.
    xf (np.ndarray): The frequency bins corresponding to the FFT results.
    fs (int): The sampling frequency of the audio signal.
    notes (list): A list of the top notes, where each note is represented as a list 
                  containing the frequency, note name, and amplitude.
    dimensions (tuple): The dimensions of the plot (width, height). Default is (960, 540).

    Returns:
    go.Figure: A Plotly Figure object representing the FFT plot.
    """
    layout = go.Layout(
        title="frequency spectrum",
        autosize=False,
        width=dimensions[0],
        height=dimensions[1],
        xaxis_title="Frequency (note)",
        yaxis_title="Magnitude",
        font={'size': 24},
        paper_bgcolor='rgb(128, 128, 128)',
        plot_bgcolor='rgb(192, 192, 192)'
    )

    fig = go.Figure(layout=layout,
                    layout_xaxis_range=[FREQ_MIN, FREQ_MAX],
                    layout_yaxis_range=[0, 1]
                    )

    fig.add_trace(go.Scatter(
        x=xf,
        y=p,
        line=dict(color='rgb(0, 0, 205)'),
        fill='toself',
        fillcolor='rgba(173, 216, 230, 0.1)'
    ))

    for note in notes:
        fig.add_annotation(x=note[0]+10, y=note[2],
                           text=note[1],
                           font={'size': 48},
                           showarrow=False)
    return fig

def extract_sample(audio: np.ndarray, frame_number: int, frame_offset: int, fft_window_size: int) -> np.ndarray:
    """
    Extracts a sample from the audio for a given frame number.
    
    Parameters:
    audio (np.ndarray): The audio signal array.
    frame_number (int): The current frame number.
    frame_offset (int): The offset between frames in the audio signal.
    fft_window_size (int): The size of the FFT window.
    
    Returns:
    np.ndarray: The extracted audio sample.
    """
    end = frame_number * frame_offset
    begin = int(end - fft_window_size)

    if end == 0:
        return np.zeros((np.abs(begin)), dtype=float)
    elif begin < 0:
        return np.concatenate([np.zeros((np.abs(begin)), dtype=float), audio[0:end]])
    else:
        return audio[begin:end]

def find_top_notes(fft: np.ndarray, xf: np.ndarray, num: int) -> list:
    """
    Identify the top musical notes from the FFT results.
    Parameters:
    fft (numpy.ndarray): The FFT result array containing complex numbers.
    xf (numpy.ndarray): The frequency bins corresponding to the FFT results.
    num (int): The number of top notes to find.
    Returns:
    list: A list of the top `num` notes, where each note is represented as a list 
          containing the frequency, note name, and amplitude.
          Returns an empty list if the maximum real part of the FFT is less than 0.001.
    """
    if np.max(fft.real) < 0.001:
        return []

    lst = [x for x in enumerate(fft.real)]
    lst = sorted(lst, key=lambda x: x[1], reverse=True)

    idx = 0
    found = []
    found_note = set()
    while (idx < len(lst)) and (len(found) < num):
        f = xf[lst[idx][0]]
        y = lst[idx][1]
        n = freq_to_number(f)
        n0 = int(round(n))
        name = note_name(n0)

        if name not in found_note:
            found_note.add(name)
            s = [f, name, y]
            found.append(s)
        idx += 1

    return found

def clear_frames_directory(frames_dir):
    """
    Clears the frames directory by deleting all files and subdirectories within it.
    
    Parameters:
    frames_dir (str): The path to the frames directory.
    
    Returns:
    None
    """
    if os.path.exists(frames_dir) and os.listdir(frames_dir):
        logger.info(f"Deleting old frames in {frames_dir}")
        for filename in os.listdir(frames_dir):
            file_path = os.path.join(frames_dir, filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            except Exception as e:
                logger.error(f"Failed to delete {file_path}. Reason: {e}")

def generate_video():
    """
    Generates a video visualization of an audio file using FFT (Fast Fourier Transform) analysis.
    This function reads an audio file, performs FFT on segments of the audio to extract frequency
    information, and generates frames for a video visualization. The frames are then combined with
    the audio to produce a video file.
    Steps:
    1. Read the audio file and calculate necessary parameters.
    2. Perform a first pass to determine the maximum amplitude for normalization.
    3. Perform a second pass to generate frames for the video.
    4. Combine the frames and audio into a video using FFmpeg.
    Parameters:
    None
    Returns:
    None
    Raises:
    subprocess.CalledProcessError: If there is an error running the FFmpeg command.
    Notes:
    - The function uses global variables for configuration such as AUDIO_FILE, FPS, FFT_WINDOW_SECONDS,
      TOP_NOTES, FRAMES_DIR, SCALE, and VIDEO_FILE.
    - The function assumes the existence of helper functions: extract_sample, find_top_notes, and plot_fft.
    - FFmpeg must be installed and available in the system's PATH.
    """
    fs, audio = wavfile.read(AUDIO_FILE)
    
    audio_length = len(audio)/fs
    frame_count = int(audio_length*FPS)
    frame_offset = int(len(audio)/frame_count)
    fft_window_size = int(fs * FFT_WINDOW_SECONDS)
    
    window = 0.5 * (1 - np.cos(np.linspace(0, 2*np.pi, fft_window_size, False)))
    xf = np.fft.rfftfreq(fft_window_size, 1/fs)

    # Pass 1, find out the maximum amplitude so we can scale (normalization)
    mx = 0
    for frame_number in range(frame_count):
        sample = extract_sample(audio, frame_number, frame_offset, fft_window_size)

        fft = np.fft.rfft(sample * window)
        fft = np.abs(fft).real 
        mx = max(np.max(fft),mx)

    logger.info(f"Max amplitude: {mx}")

    # Clear the frames directory to remove old frames from previous runs
    clear_frames_directory(FRAMES_DIR)
    
    # Pass 2, produce the animation
    for frame_number in tqdm(range(frame_count)):
        sample = extract_sample(audio, frame_number, frame_offset, fft_window_size)
        fft = np.fft.rfft(sample * window)
        fft = np.abs(fft) / mx
        
        s = find_top_notes(fft, xf, TOP_NOTES)
        
        fig = plot_fft(fft.real, xf, fs, s, RESOLUTION)
        fig.write_image(f"{FRAMES_DIR}/frame{frame_number}.png", scale=SCALE)

    ffmpeg_command = f"ffmpeg -y -r {FPS} -f image2 -s 1920x1080 -i {FRAMES_DIR}/frame%d.png -i {AUDIO_FILE} -c:v libx264 -pix_fmt yuv420p {VIDEO_FILE}"
    
    try:
        result = subprocess.run(ffmpeg_command, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        logger.info("FFmpeg Output: %s", result.stdout)
    except subprocess.CalledProcessError as e:
        logger.error("Error running FFmpeg: %s", e)
        logger.error("FFmpeg Error Output: %s", e.stderr)