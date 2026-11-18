"""Letters for the year ahead. Content reaches the page only through compose_page."""

from pathlib import Path

import streamlit as st

from data.letters_2027 import LETTERS, SETTINGS
from logic.clock import current_clock, query_value
from logic.photos import (
    list_image_files,
    polaroid_from_path,
    read_captions,
    safe_photo_path,
    wall_html,
)
from logic.render import compose_page, dare_rule_html, header_html, safe_accent
from logic.songs import classify_song
from logic.unlock import year_is_open

ROOT = Path(__file__).resolve().parents[1]
KOREA_DIR = ROOT / "assets" / "korea"


def show_html(fragment: str) -> None:
    if not fragment:
        return
    st.html(fragment, width="stretch")


def wind_rain(
    emojis=("🪩", "🥂"),
    count=30,
    min_size=14,
    max_size=34,
    min_duration=9,
    max_duration=10,
    max_drift_vw=25,
    z_index=999999,
):
    # Injected into this page (st.html is not an iframe). Same overlay id the
    # older years remove when you leave, so the snow doesn't follow you.
    html = f"""
    <script>
    (function() {{
      const doc = document;
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
        const left = rand(-5, 105);
        const delay = rand(0, 6);
        const dur = rand(minDur, maxDur);
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
    st.html(html, unsafe_allow_javascript=True, width="content")


def render_song(url: str) -> None:
    try:
        kind, value = classify_song(url)
    except Exception:
        return
    if kind == "none" or not value:
        return
    try:
        if kind == "spotify":
            height = 152 if "/track/" in value or "/episode/" in value else 352
            st.iframe(value, height=height)
        elif kind == "youtube":
            st.iframe(value, height=360)
        elif kind == "link":
            st.link_button("Play the song", value)
    except Exception:
        st.caption("The song couldn't be embedded.")


def render_photos(photos: tuple[str, ...]) -> None:
    if not photos:
        return
    for rel in photos:
        try:
            path = safe_photo_path(ROOT, rel)
        except Exception:
            path = None
        if path is None:
            st.caption("One photo for this letter is missing.")
            continue
        try:
            st.image(str(path), width="stretch")
        except Exception:
            st.caption("One photo for this letter couldn't be shown.")


def load_korea() -> str:
    captions, error = read_captions(KOREA_DIR / "captions.toml")
    shots = []
    for path in list_image_files(KOREA_DIR):
        caption = captions.get(path.name, "")
        shot = polaroid_from_path(path, caption)
        if shot is not None:
            shots.append(shot)
    return wall_html(
        str(SETTINGS.get("korea_title") or ""),
        str(SETTINGS.get("korea_dates") or ""),
        str(SETTINGS.get("korea_note") or ""),
        shots,
        error,
    )


try:
    clock = current_clock()
    open_year = year_is_open(
        clock.instant,
        SETTINGS["page_unlock"],
        SETTINGS["page_timezone"],
    )
except Exception:
    st.stop()

if not open_year:
    st.stop()

accent = safe_accent(str(SETTINGS.get("accent") or ""))
css = (ROOT / "style" / "y2027.css").read_text(encoding="utf-8")
# @import has to stay the first rule in the stylesheet.
show_html(f"<style>\n{css}\n:root, .stApp {{ --accent: {accent}; }}\n</style>")
wind_rain()

requested = query_value(st.query_params, "open")
animate = bool(requested) and st.session_state.get("ny27_played") != requested
keep = {}
if clock.previewing and clock.preview_value and clock.key_value:
    keep = {"preview": clock.preview_value, "key": clock.key_value}

bits = compose_page(
    LETTERS,
    clock.instant,
    str(SETTINGS.get("default_timezone") or "Asia/Singapore"),
    requested,
    keep,
    str(SETTINGS.get("heart") or "🤍"),
    animate,
)
if not bits.grid_html:
    st.caption("The envelopes couldn't be laid out.")
    st.stop()

if bits.opened_id:
    st.session_state["ny27_played"] = bits.opened_id
else:
    st.session_state.pop("ny27_played", None)

show_html(
    header_html(
        str(SETTINGS.get("headline") or ""),
        str(SETTINGS.get("heart") or ""),
        str(SETTINGS.get("intro") or ""),
        clock.banner if clock.previewing else None,
    )
)

if bits.letter_html:
    show_html(bits.letter_html)
    render_song(bits.song)
    render_photos(bits.photos)

show_html(bits.grid_html)
show_html(dare_rule_html())

prompt = str(
    SETTINGS.get("reveal_prompt")
    or "click only if you're daring enough to see whats on the other side"
)
if st.toggle(prompt):
    show_html(load_korea())
