from pathlib import Path
import json
import streamlit as st
from streamlit_lottie import st_lottie
from streamlit_extras.let_it_rain import rain
import streamlit.components.v1 as components

THIS_DIR = Path(__file__).parent.parent
CSS_FILE = THIS_DIR / "style" / "style.css"
ASSETS = THIS_DIR / "assets"
LOTTIE_ANIMATION = ASSETS / "animation1.json"

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

def load_lottie_animation(file_path):
    with open(file_path, "r") as f:
        return json.load(f)

def run_snow_animation():
    rain(emoji= "🥂", font_size=20, falling_speed=5, animation_length="infinite")

#def get_person_name():
    #query_params = st.experimental_get_query_params()
    #return query_params.get("name", ["Friend"])[0]

#st.set_page_config(page_title="Happy New Year!", page_icon="🥳")

run_snow_animation()

with open(CSS_FILE) as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

#PERSON_NAME = get_person_name()
st.markdown("<h1 style='text-align: center; color: white;'>Happy New Year, Elfie!🪩</h1>", unsafe_allow_html=True)

lottie_animation = load_lottie_animation(LOTTIE_ANIMATION)
st_lottie(lottie_animation, key="lottie-holiday", height= 300)

st.video('https://www.youtube.com/embed/gEHCXl4J9Qo?', format="video/mp4", start_time=10)

multi1 = '''Hope you'll get your reputation🐍(ts version) today/tmr as well as for all your wishes to come true in 2024!!

Here's to a better year ahead!!🥳🎊 (Greatest academic comeback of all time maybe?)'''

st.markdown(multi1)

multi2 = '''And also just in case I've not said it.
I'm really greatful to have met you last year, it was truly a highlight of mine in 2023!'''

st.markdown(multi2)

st.write("[Only click this link if you are brave enough to see what's on the other side](https://youtu.be/hvL1339luv0?si=zEBYoql2lf-iPU6j)")