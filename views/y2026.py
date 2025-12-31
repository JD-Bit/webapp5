import json
from pathlib import Path
import pandas as pd
import streamlit as st
import plotly.graph_objects as go
import base64
from streamlit_lottie import st_lottie
from streamlit_extras.let_it_rain import rain
import streamlit.components.v1 as components

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700&display=swap');

.romantic-header {
    font-family: 'Playfair Display', serif;
    font-size: 3.0rem;
    text-align: center;
    color: #ffffff;
    letter-spacing: 1px;
    margin-top: 1.2rem;
    margin-bottom: 1.8rem;
    text-shadow: 
        0 0 8px rgba(255,255,255,0.25),
        0 0 16px rgba(255,255,255,0.15);
}
</style>
""", unsafe_allow_html=True)


# Pure black MAIN AREA only (sidebar unchanged)
st.markdown("""
<style>
/* Main content area background */
.stApp {
    background-color: #000000 !important;
    color: #ffffff !important;
}

/* The central content container (extra safety) */
section.main > div {
    background-color: #000000 !important;
}

/* Text colors in main area */
section.main h1, section.main h2, section.main h3, section.main h4,
section.main p, section.main span, section.main div, section.main label {
    color: #ffffff !important;
}

/* Metric cards (main area only) */
section.main [data-testid="stMetric"] {
    background-color: #000000 !important;
    border: 1px solid rgba(255,255,255,0.15);
    border-radius: 14px;
    padding: 10px;
}

/* Dataframe container (main area only) */
section.main [data-testid="stDataFrame"] {
    background-color: #000000 !important;
}

/* Divider */
section.main hr {
    border-color: rgba(255,255,255,0.2) !important;
}
</style>
""", unsafe_allow_html=True)

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



# File paths
THIS_DIR = Path(__file__).parent.parent
ASSETS = THIS_DIR / "assets"
LOTTIE_ANIMATION = ASSETS / "animation3.json"
AUDIO_FILE = ASSETS / "audio.mp3"
DATA_DIR  = THIS_DIR / "assets"
#LINK_AUDIO_FILE = ASSETS / "link_audio.mp3"
#IMAGE_FILE = ASSETS / "image1.jpeg"

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

# Run snow animation
def wind_rain(
    emojis=("🪩", "🥂", "✨"),
    count=40,
    min_size=14,
    max_size=34,
    min_duration=5,
    max_duration=14,
    max_drift_vw=22,
    z_index=999999
):
    # NOTE: we inject into window.parent.document so it overlays the Streamlit app.
    html = f"""
    <script>
    (function() {{
      const doc = window.parent.document;

      // Remove existing overlay if rerun
      const old = doc.getElementById("wind-rain-overlay");
      if (old) old.remove();

      const overlay = doc.createElement("div");
      overlay.id = "wind-rain-overlay";
      overlay.style.position = "fixed";
      overlay.style.inset = "0";
      overlay.style.pointerEvents = "none";
      overlay.style.zIndex = "{z_index}";
      overlay.style.overflow = "hidden";
      overlay.style.background = "transparent";
      doc.body.appendChild(overlay);

      const emojis = {list(emojis)};
      const count = {count};
      const minSize = {min_size};
      const maxSize = {max_size};
      const minDur  = {min_duration};
      const maxDur  = {max_duration};
      const maxDrift = {max_drift_vw};

      function rand(a,b) {{ return a + Math.random()*(b-a); }}
      function choice(arr) {{ return arr[Math.floor(Math.random()*arr.length)]; }}

      for (let i = 0; i < count; i++) {{
        const el = doc.createElement("div");
        el.textContent = choice(emojis);

        const size = rand(minSize, maxSize);
        const left = rand(-5, 105);       // vw
        const delay = rand(0, 6);         // seconds
        const dur = rand(minDur, maxDur); // seconds
        const drift = (Math.random() < 0.5 ? -1 : 1) * rand(0, maxDrift);
        const wobble = rand(6, 18);

        el.style.position = "absolute";
        el.style.left = left + "vw";
        el.style.top = "-10vh";
        el.style.fontSize = size + "px";
        el.style.opacity = rand(0.7, 1.0);
        el.style.filter = "drop-shadow(0 0 6px rgba(255,255,255,0.15))";

        const animName = "wr_anim_" + i;

        const style = doc.createElement("style");
        style.textContent = `
          @keyframes ${"{animName}"} {{
            0%   {{ transform: translate(0, 0); }}
            25%  {{ transform: translate(${ "{drift}" }*0.25vw, 25vh) translateX(${ "{wobble}" }px); }}
            50%  {{ transform: translate(${ "{drift}" }*0.55vw, 50vh) translateX(-${ "{wobble}" }px); }}
            75%  {{ transform: translate(${ "{drift}" }*0.85vw, 75vh) translateX(${ "{wobble}" }px); }}
            100% {{ transform: translate(${ "{drift}" }vw, 110vh); }}
          }}
        `;
        doc.head.appendChild(style);

        el.style.animation = animName + " " + dur + "s linear " + delay + "s infinite";
        overlay.appendChild(el);
      }}
    }})();
    </script>
    """
    # Give it a tiny height; it only exists to run the script
    components.html(html, height=1, width=1)


wind_rain(emojis=("🪩","🥂"), count=30, min_duration=9, max_duration=10, max_drift_vw=25)



# Display Lottie animation
st.markdown(
    "<div class='romantic-header'>HAPPY NEW YEAR MY SIGNIFICANT OTHER 😘</div>",
    unsafe_allow_html=True
)

lottie_animation = load_lottie_animation(LOTTIE_ANIMATION)
st_lottie(lottie_animation, key="lottie-holiday")

# Play background audio without the audio bar
autoplay_audio(AUDIO_FILE)

# ------------------
# Load data
# ------------------
df = pd.read_parquet(DATA_DIR / "messages.parquet")
df["dt"] = pd.to_datetime(df["dt"])

with open(DATA_DIR / "meta.json", "r", encoding="utf-8") as f:
    meta = json.load(f)

streaks = pd.read_parquet(DATA_DIR / "streaks.parquet")
affection = pd.read_parquet(DATA_DIR / "affection.parquet")

# ------------------
# Header + KPIs
# ------------------
#if st.toggle("Here is a tiny year-in-review built from our Telegram messages "): 
# --- derived stats ---
longest = streaks.sort_values("days", ascending=False).iloc[0]

total_msgs = int(meta["num_messages"])
days_with_msgs = int(df["dt"].dt.date.nunique())
first_day = meta["min_dt"][:10]
last_day = meta["max_dt"][:10]

rel = meta["relationship_as_dataset"]

# Love signals
a = affection.set_index("sender")
jiade = a.loc["Jiade"]
elfie = a.loc["Elfie💕"]

total_affection = int(jiade["total_affection"] + elfie["total_affection"])

# --- merged love letter ---
st.markdown(
    f"""
<div style="line-height:1.9; font-size:1.15rem; max-width: 820px; margin: auto;">

<p>
Hii my beautiful hottie,<br>
this year began quietly, just two people, a phone screen, and the kind of conversations
that slowly turn into something even greater.
From <b>{first_day}</b> to <b>{last_day}</b>,
we kept finding our way back to each other, no matter what.
</p>

<p>
We sent a total of <b>{total_msgs:,}</b> messages this year.
That’s thousands of little moments consisting of
late-night thoughts, inside jokes,
“I miss you”s, and “I love you”s that would’ve made it straight into a lyric notebook.
</p>

<p>
We talked on all <b>{days_with_msgs}</b> days.
No disappearing acts. No off-season.
Just us, showing up again and again,
like a chorus you never skip.
</p>

<p>
And love showed up in the smallest, sweetest ways.
I told you “I love you” <b>{jiade['love_you']}</b> times,
and somehow it still never felt like enough. We miss each other too <3!💋
<b>{jiade['miss_you']}</b> “I miss you”s from me,
<b>{elfie['miss_you']}</b> from you!
Hearts were everywhere, kisses even more,
filling the quiet moments between messages.
</p>

<p>
Altogether, there were a total of <b>{total_affection}</b> tiny acts of love this year.
It was not loud nor flashy. Just consistent, soft, and always us.
</p>

<p>
If our love story were written like a Taylor Swift discography,
it would fill <b>{rel['pages_equivalent']}</b> lyric pages —
basically <b>{rel['novels_equivalent']}</b> full albums worth of words,
feelings, and moments we’ll always come back to.
</p>

<p style="margin-top:1.6rem; text-align:center; font-weight:600;">
No skips. No bad tracks.<br>
Just us — <b>Our Year</b> 💿✨
</p>

</div>
""",
    unsafe_allow_html=True
)

# ======================================================
# 1) THE YEAR AT A GLANCE (CALENDAR + STREAK)
# ======================================================
if st.toggle("Our Year at a Glance"):
    # Daily counts
    daily = df.copy()
    daily["date"] = daily["dt"].dt.normalize()
    daily_counts = daily.groupby("date").size().reset_index(name="messages")

    all_days = pd.date_range(
        daily_counts["date"].min(),
        daily_counts["date"].max(),
        freq="D"
    )

    calendar_df = (
        pd.DataFrame({"date": all_days})
        .merge(daily_counts, on="date", how="left")
        .fillna({"messages": 0})
    )
    calendar_df["messages"] = calendar_df["messages"].astype(int)

    calendar_df["weekday"] = calendar_df["date"].dt.weekday
    calendar_df["week"] = calendar_df["date"] - pd.to_timedelta(
        calendar_df["weekday"], unit="D"
    )

    calendar_df["hover"] = (
        calendar_df["date"].dt.strftime("%Y-%m-%d")
        + "<br>Messages: "
        + calendar_df["messages"].astype(str)
    )

    heatmap = (
        calendar_df
        .pivot(index="weekday", columns="week", values="messages")
        .sort_index(ascending=False)
    )

    fig = go.Figure(
        data=go.Heatmap(
            z=heatmap.values,
            x=heatmap.columns,
            y=["Sun","Sat","Fri","Thu","Wed","Tue","Mon"],
            colorscale="Viridis",
            hoverinfo="text",
            text=[
                [
                    calendar_df.loc[
                        (calendar_df["week"] == col)
                        & (calendar_df["weekday"] == (6 - row)),
                        "hover"
                    ].values[0]
                    if len(calendar_df.loc[
                        (calendar_df["week"] == col)
                        & (calendar_df["weekday"] == (6 - row))
                    ]) > 0 else ""
                    for col in heatmap.columns
                ]
                for row in range(7)
            ],
        )
    )

    fig.update_layout(height=300, margin=dict(l=20, r=20, t=30, b=20))
    st.plotly_chart(fig, use_container_width=True)

    st.write('''Throughout the year, there were many firsts too, from the first time I gave you flowers, to the first time we met each other's family! 
    All these firsts are filled with joy and happiness and I'm sure it will not be out last! Looking forward to many other first's with you! 
    I LOVE YOU SOSOSO MUCH BABYY. YOU ARE THE MOST CAPABLE, BEATIFUL, AMAZING, HOT, WONDERFUL, SWEET, LOVING, PRETTIST AND PERFECT GIRL IN THE WHOLE UNIVERSE!! 
    I am indeed the luckiest guy in the world to be able to be your boyfriend and I would'nt wanna trade anything for it! YOU ARE MY ONE AND ONLY BABYY! AND HERES TO ANOTHER YEAR OF ENDLESS LAUGHTER, THOUSANDS OF SMALL MOMENTS AND A WHOLE LOT OF CORE MEMORIES WITH YOU💋😘💕 ''' )



