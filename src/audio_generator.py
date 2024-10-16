import os
import sys
import torch
import torchaudio
from audiocraft.models import MusicGen
from .config import SAMPLE_RATE, AUDIO_DURATION, AUDIO_FILE

sys.path.append(os.path.join(os.path.dirname(__file__), 'audiocraft'))

from audiocraft.models import MusicGen

def load_model():
    return MusicGen.get_pretrained('facebook/musicgen-small')

def generate_music_tensors(description: str, model: MusicGen, duration: int = AUDIO_DURATION) -> torch.Tensor:
    """
    Generates music tensors based on a given description using the specified model.

    Args:
        description (str): A textual description of the music to be generated.
        model (MusicGen): The pre-trained MusicGen model to use for generation.
        duration (int, optional): The duration of the generated music in seconds. Defaults to AUDIO_DURATION.

    Returns:
        torch.Tensor: A tensor containing the generated music samples.
    """
    model.set_generation_params(
        use_sampling=True,
        top_k=250,
        duration=duration
    )

    output = model.generate(
        descriptions=[description],
        progress=True,
        return_tokens=True
    )

    return output[0]

def save_audio(samples: torch.Tensor):
    """
    Renders an audio player for the given audio samples and saves them to a local directory.

    Args:
        samples (torch.Tensor): A tensor of decoded audio samples with shapes [B, C, T] or [C, T].
    """

    print("Samples (inside function): ", samples)
    sample_rate = 32000
    save_path = "audio_output/"
    assert samples.dim() == 2 or samples.dim() == 3

    samples = samples.detach().cpu()
    if samples.dim() == 2:
        samples = samples[None, ...]

    for idx, audio in enumerate(samples):
        audio_path = os.path.join(save_path, f"audio_{idx}.wav")
        torchaudio.save(audio_path, audio, sample_rate)