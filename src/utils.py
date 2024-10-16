import base64
import os
import numpy as np
from .config import NOTE_NAMES

def get_binary_file_downloader_html(bin_file: str, file_label: str = 'File') -> str:
    """
    Generates an HTML link for downloading a binary file.

    Args:
        bin_file (str): The path to the binary file to be downloaded.
        file_label (str): The label for the download link. Defaults to 'File'.

    Returns:
        str: An HTML string containing the download link.
    """
    with open(bin_file, 'rb') as f:
        data = f.read()
    bin_str = base64.b64encode(data).decode()
    href = f'<a href="data:application/octet-stream;base64,{bin_str}" download="{os.path.basename(bin_file)}">Download {file_label}</a>'
    return href

def freq_to_number(f): return 69 + 12*np.log2(f/440.0)
def number_to_freq(n): return 440 * 2.0**((n-69)/12.0)
def note_name(n): return NOTE_NAMES[n % 12] + str(int(n/12 - 1))