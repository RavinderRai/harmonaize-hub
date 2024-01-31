# HarmonAIzeHub

This is a simple app that generates music from text and visualizes the output in a video, showing the music. Here is an example of what this will look like:

![Streamlit Screenshot](MusicGenExampleImage.jpg)

The app uses the new facebook research audiocraft libraries to generate music from text - specifically using the small model. Then it visualizes the notes being played using fast fourier transforms. 

The image above shows you can input some text to generate your music, and then you will see the video populate and can watch/listen to it immediately. Note it does take about a minute to generate the music. Also keep in mind the visualization works best for solo instruments, so best to indicate the in the text when generating music. 
