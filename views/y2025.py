import base64
import streamlit as st
import json
from pathlib import Path
from streamlit_lottie import st_lottie
from streamlit_extras.let_it_rain import rain
import streamlit.components.v1 as components

def clear_wind_rain():
    components.html("""
    <script>
    (function() {
      const doc = window.parent.document;
      const old = doc.getElementById("wind-rain-overlay");
      if (old) old.remove();
    })();
    </script>
    """, height=1, width=1)

clear_wind_rain()

# Function to load a Lottie animation
def load_lottie_animation(file_path):
    with open(file_path, "r") as f:
        return json.load(f)

# Function to autoplay audio without displaying the audio bar
def autoplay_audio(file_path: str, file_type: str = "audio/mp3"):
    try:
        with open(file_path, "rb") as f:
            data = f.read()
            b64 = base64.b64encode(data).decode()
            md = f"""
                <audio autoplay="true" loop style="display:none;">
                    <source src="data:{file_type};base64,{b64}" type="{file_type}">
                </audio>
            """
            st.markdown(md, unsafe_allow_html=True)
    except FileNotFoundError:
        st.error("Audio file not found. Please check the file path.")

# Function to embed clickable audio
def embed_audio(audio_file_path):
    try:
        with open(audio_file_path, "rb") as f:
            audio_bytes = f.read()
            st.audio(audio_bytes, format="audio/mp3")
    except FileNotFoundError:
        st.error("Audio file not found. Please check the file path.")


# Function to run snow animation
def run_snow_animation():
    rain(emoji="🪩", font_size=20, falling_speed=5, animation_length="infinite")

# File paths
THIS_DIR = Path(__file__).parent.parent
ASSETS = THIS_DIR / "assets"
LOTTIE_ANIMATION = ASSETS / "animation2.json"
AUDIO_FILE = ASSETS / "audio.mp3"
LINK_AUDIO_FILE = ASSETS / "link_audio.mp3"
IMAGE_FILE = ASSETS / "image1.jpeg"

# Run snow animation
run_snow_animation()

# Display Lottie animation
st.markdown("<h1 style='text-align: center; color: white;'>HAPPY NEW YEAR BABYY😘</h1>", unsafe_allow_html=True)

lottie_animation = load_lottie_animation(LOTTIE_ANIMATION)
st_lottie(lottie_animation, key="lottie-holiday", height=600)

# Play background audio without the audio bar
autoplay_audio(AUDIO_FILE)

# Messages
multi1 = '''Can you believe it, a year has past since I sent you this very link!

Looking back on 2024, I dare say it is the best year of my life and its all because of you! YOU ARE MY WHOLE UNIVERSE WIFEY❣️ Thank you once again for letting me
be your boyfriend, IM TRULY THE LUCKIEST GUY IN THE WHOLE UNIVERSE!! We have made so many fond memories together and I cant wait to create more of them this year with you and only you💕

Spending time with you has been the highlight of my year, and I'm forever grateful for every single second of it!

I LOVE YOU SOSOSOOSOSOSOSOSOSOSOSOSOSOSOSOSOSOSOSOSOSOSOSOSOSOSOSOSOSOS0SOSOSOOSOSOSOSOSOSOSOSOSOSOSOSOSOSOSOSOSOSOSOSOSOSOSOSOSOSOS0SOSOSOOSOSOSOSOSOSOSOSOSOSOSOSOSOSOSOSOSOSOSOSOSOSOSOSOSOSOS0SOSOSOOSOSOSOSOSOSOSOSOSOSOSOSOSOSOSOSOSOSOSOSOSOSOSOSOSOSOS0SOSOSOOSOSOSOSOSOSOSOSOSOSOSOSOSOSOSOSOSOSOSOSOSOSOSOSOSOSOS0SOSOSOOSOSOSOSOSOSOSOSOSOSOSOSOSOSOSOSOSOSOSOSOSOSOSOSOSOSOS0SOSOSOOSOSOSOSOSOSOSOSOSOSOSOSOSOSOSOSOSOSOSOSOSOSOSOSOSOSOS0SOSOSOOSOSOSOSOSOSOSOSOSOSOSOSOSOSOSOSOSOSOSOSOSOSOSOSOSOSOS0SOSOSOOSOSOSOSOSOSOSOSOSOSOSOSOSOSOSOSOSOSOSOSOSOSOSOSOSOSOS0SOSOSOOSOSOSOSOSOSOSOSOSOSOSOSOSOSOSOSOSOSOSOSOSOSOSOSOSOSOS0SOSOSOOSOSOSOSOSOSOSOSOSOSOSOSOSOSOSOSOSOSOSOSOSOSOSOSOSOSOS0SOSOSOOSOSOSOSOSOSOSOSOSOSOSOSOSOSOSOSOSOSOSOSOSOSOSOSOSOSOS0SOSOSOOSOSOSOSOSOSOSOSOSOSOSOSOSOSOSOSOSOSOSOSOSOSOSOSOSOSOS0SOSOSOOSOSOSOSOSOSOSOSOSOSOSOSOSOSOSOSOSOSOSOSOSOSOSOSOSOSOS0SOSOSOOSOSOSOSOSOSOSOSOSOSOSOSOSOSOSOSOSOSOSOSOSOSOSOSOSOSOS0SOSOSOOSOSOSOSOSOSOSOSOSOSOSOSOSOSOSOSOSOSOSOSOSOSOSOSOSOSOS0SOSOSOOSOSOSOSOSOSOSOSOSOSOSOSOSOSOSOSOSOSOSOSOSOSOSOSOSOSOS0SOSOSOOSOSOSOSOSOSOSOSOSOSOSOSOSOSOSOSOSOSOSOSOSOSOSOSOSOSO
MUCHHH WIFEYY! MUACKKKS

P.S MANIFESTING THAT REPUTATION(TS VERSION) WILL COME OUT THIS YEAR🔥'''
st.markdown(multi1)


if st.toggle("click only if you're daring enough to see whats on the other side HEHE"): 
    st.image(IMAGE_FILE, caption="your hand in mine - life's simplest luxury.")
    st.write("With your hand in mine, the world seems to fade away, and all that matters is us. Here's to another year of love, laughter and endless adventures with you babyyy🥂") 
    embed_audio(LINK_AUDIO_FILE)
