import streamlit as st
from pathlib import Path

st.set_page_config(page_title="Happy New Year!", page_icon="🥳")

THIS_DIR = Path(__file__).parent
page2k26 = THIS_DIR / "views" / "y2026.py"
page2k25 = THIS_DIR / "views" / "y2025.py"
page2k24 = THIS_DIR / "views" / "y2024.py"




page2024 = st.Page(
    page = page2k24,
    title = "2024",
    icon = "💙",
)

page2025 = st.Page(
    page = page2k25,
    title = "2025",
    icon = "🩷"
)

page2026 = st.Page(
    page = page2k26,
    title = "2026",
    icon = "💜",
    default=True,
)

pg = st.navigation(pages=[page2026, page2025, page2024])
logo_path = "/Users/jd/CS/webapp/app3/assets/logo.png"
st.logo(logo_path)
st.sidebar.text("HI THERE HOTTIE😍😍")
st.sidebar.image(logo_path, width=200)  # Adjust the width as needed

pg.run()