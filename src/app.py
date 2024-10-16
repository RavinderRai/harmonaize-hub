import streamlit as st
from .audio_generator import load_model, generate_music_tensors, save_audio
from .visualizer import generate_video
from .utils import get_binary_file_downloader_html
from .config import AUDIO_FILE, VIDEO_FILE



def set_page_configuration():
    st.set_page_config(
        layout='wide',
        page_icon="musical_note",
        page_title="HarmonAIze Hub"
    )

@st.cache_resource
def get_model():
    return load_model()

def apply_custom_css():
    st.markdown("""
        <style>
        .title {
            text-align: center;
            font-size: 3em;
            font-weight: bold;
            margin-top: 0;
            padding: 10px;
        }
        .description {
            text-align: center;
            font-size: 1.2em;
            margin-bottom: 30px;
            max-width: 800px;
            margin-left: auto;
            margin-right: auto;
        }
        .main-column {
            padding: 20px;
        }
        </style>
    """, unsafe_allow_html=True)

def main():
    apply_custom_css()
    
    st.markdown('<h1 class="title">HarmonAIze Hub</h1>', unsafe_allow_html=True)
    st.markdown('<p class="description">Compose and Visualize AI-Generated Music from Text! Powered by Meta’s Music Gen model, this tool generates music and visualizes it with a breakdown of the notes being played.</p>', unsafe_allow_html=True)

    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.write("")
        text_area = st.text_area(
            "Enter a description (works best with solo instruments, e.g., 'solo piano in a jazz style'):", 
            value='solo piano music in a jazz style',
            key="text_input"
        )
        
        duration = st.slider("Duration (seconds)", 10, 30, 10, 1)
        
        generate_button = st.button("Generate Music")

    with col2:
        subheader_container = st.empty()
        if generate_button:
            subheader_container.subheader("Generating Music...")
            
            with st.spinner("Generating Music..."):
                model = get_model()
                music_tensors = generate_music_tensors(text_area, model, duration)
                save_audio(music_tensors)
            
            with st.spinner("Generating Video..."):
                generate_video()

            subheader_container.subheader("Generated Music")
    
            video_file = open(VIDEO_FILE, 'rb').read()
            st.video(video_file)
            st.markdown(get_binary_file_downloader_html(AUDIO_FILE, 'Audio'), unsafe_allow_html=True)

if __name__ == "__main__":
    set_page_configuration()
    main()