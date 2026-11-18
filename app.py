import streamlit as st
from pathlib import Path

from data.letters_2027 import SETTINGS
from logic.clock import current_clock
from logic.unlock import sidebar_plan, year_is_open

st.set_page_config(page_title="Happy New Year!", page_icon="🥳")

THIS_DIR = Path(__file__).parent
paths = {
    "2024": THIS_DIR / "views" / "y2024.py",
    "2025": THIS_DIR / "views" / "y2025.py",
    "2026": THIS_DIR / "views" / "y2026.py",
    "2027": THIS_DIR / "views" / "y2027.py",
}

# 2027 stays out of the sidebar until 1 Jan 2027, 00:00 Asia/Singapore.
# Preview (?preview=YYYY-MM-DD&key=...) can open it sooner, and only with the
# secret in .streamlit/secrets.toml. If the clock fails, 2026 stays the default.
show_2027 = False
try:
    clock = current_clock()
    show_2027 = year_is_open(
        clock.instant,
        SETTINGS["page_unlock"],
        SETTINGS["page_timezone"],
    )
except Exception:
    show_2027 = False

pages = []
for item in sidebar_plan(show_2027, SETTINGS["heart"]):
    kwargs = {
        "page": paths[item["title"]],
        "title": item["title"],
        "icon": item["icon"],
    }
    if item["default"]:
        kwargs["default"] = True
    pages.append(st.Page(**kwargs))

pg = st.navigation(pages=pages)
logo_path = "assets/logo.png"
st.logo(logo_path)
st.sidebar.text("HI THERE HOTTIE😍😍")
st.sidebar.image(logo_path, width=200)  # Adjust the width as needed

pg.run()
