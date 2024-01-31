from audiocraft.models import MusicGen
import streamlit as st 
import torch 
import torchaudio
import os 
import numpy as np
import base64
import subprocess

@st.cache_resource
def load_model():
    model = MusicGen.get_pretrained('facebook/musicgen-small')
    return model

def generate_music_tensors(description, duration: int):
    print("Description: ", description)
    print("Duration: ", duration)
    model = load_model()

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
    """Renders an audio player for the given audio samples and saves them to a local directory.

    Args:
        samples (torch.Tensor): a Tensor of decoded audio samples
            with shapes [B, C, T] or [C, T]
        sample_rate (int): sample rate audio should be displayed with.
        save_path (str): path to the directory where audio should be saved.
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

def get_binary_file_downloader_html(bin_file, file_label='File'):
    with open(bin_file, 'rb') as f:
        data = f.read()
    bin_str = base64.b64encode(data).decode()
    href = f'<a href="data:application/octet-stream;base64,{bin_str}" download="{os.path.basename(bin_file)}">Download {file_label}</a>'
    return href

st.set_page_config(
    layout= 'wide',
    page_icon= "musical_note",
    page_title= "Text to Music"
)

def main():
    st.title("Visualizing Generated Music from Text 🎵")

    st.write("Music Generator app built using Meta's Music Gen Small model from their Audiocraft library.")
    st.write("Output will be a video with the music alongside a visual representation of the notes being played.")

    col1, col2 = st.columns(2)
    
    with col1:
        text_area = st.text_area(
            "Enter your description here:\n\nVisual Representation works best with solo instruments.\n\nTry something like solo piano music in a jazz style for best results.", 
            value='solo piano music in a jazz style',
            key="text_input"
        )
        generate_button = st.button("Generate Music")
        
        #no time slider for now
        #time_slider = st.slider("Select time duration (In Seconds)", 0, 20, 10)

    with col2:
        subheader_container = st.empty()
        if generate_button:
    
            subheader_container.subheader("Generating Music...")
    
            #setting time to be 10 seconds and not using time slider for now
            music_tensors = generate_music_tensors(text_area, 10)
            print("Musci Tensors: ", music_tensors)
            save_music_file = save_audio(music_tensors)
            audio_filepath = 'audio_output/audio_0.wav'
    
            script_name = 'NoteSimulation.py'
    
            try:
                result = subprocess.run(['python', script_name], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
                print("Output:", result.stdout)
            except subprocess.CalledProcessError as e:
                print(f"Error running {script_name}: {e}")
                print("Error Output:", e.stderr)

            subheader_container.subheader("Generated Music")
    
            video_filepath = 'movie.mp4'
            video_file = open(video_filepath, 'rb').read()
            st.video(video_file)
            st.markdown(get_binary_file_downloader_html(audio_filepath, 'Audio'), unsafe_allow_html=True)

if __name__ == "__main__":
    main()